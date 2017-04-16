#!/usr/bin/env python
# -*- coding: utf8 -*-

from .pbxmockup import weekday
import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns
from yamlns.dateutils import Date
from scheduling import peekQueue, weekstart, nextweek, Scheduling

class Scheduling_Test(unittest.TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))

    def test_weekday_withSunday(self):
        self.assertEqual(
            'dg', weekday(Date("2017-10-01")))

    def test_weekday_withMonday(self):
        self.assertEqual(
            'dl', weekday(Date("2017-10-02")))

    def test_weekday_withWenesday(self):
        self.assertEqual(
            'dx', weekday(Date("2017-10-04")))

    def test_weekstart_withMonday(self):
        self.assertEqual(
            weekstart(Date("2017-10-02")),
            Date("2017-10-02"))

    def test_weekstart_withFriday(self):
        self.assertEqual(
            weekstart(Date("2017-10-06")),
            Date("2017-10-02"))

    def test_nextweek_withMonday(self):
        self.assertEqual(
            nextweek(Date("2017-10-02")),
            Date("2017-10-09"))

    def test_nextweek_withFriday(self):
        self.assertEqual(
            nextweek(Date("2017-10-06")),
            Date("2017-10-09"))


    def test_peekQueue_oneSlot_oneTurn(self):
        schedule = ns.loads(u"""\
            timetable:
              dl:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(peekQueue(schedule,'dl','12:00'), [
            'cesar',
            ])

    def test_peekQueue_oneSlot_twoTurns(self):
        schedule = ns.loads(u"""\
            timetable:
              'dl':
              -
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(peekQueue(schedule,'dl','12:00'), [
            'cesar',
            'eduard',
            ])


    def test_peekQueue_twoTimes(self):
        schedule = ns.loads(u"""\
            timetable:
              dl:
              -
                - cesar
              -
                - eduard
            hours:
            - '00:00'
            - '12:00'
            - '23:59'

            extensions:
              cesar: 200
              eduard: 201
            """)
        self.assertEqual(peekQueue(schedule,'dl','12:00'), [
            'eduard',
            ])

    def test_peekQueue_beforeTime(self):
        schedule = ns.loads(u"""\
            timetable:
              dl:
              -
                - cesar
            hours:
            - '23:58'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(peekQueue(schedule,'dl', '12:00'), [
            ])

    def test_peekQueue_afterTime(self):
        schedule = ns.loads(u"""\
            timetable:
              dl:
              -
                - cesar
            hours:
            - '00:00'
            - '00:01'

            extensions:
              cesar: 200
            """)
        self.assertEqual(peekQueue(schedule,'dl','12:00'), [
            ])

    def test_peekQueue_nonExistingDay(self):
        schedule = ns.loads(u"""\
            timetable:
              dm:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(peekQueue(schedule,'dl','12:00'), [
            ])

    def test_peekQueue_aDifferentDay(self):
        schedule = ns.loads(u"""\
            timetable:
              dm:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(peekQueue(schedule,'dm','12:00'), [
            'cesar',
            ])

    @unittest.skip("TODO")
    def test_peekQueue_withNobodySlots(self): pass


    def test_extension_existing(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extension('cesar'),
            '200')

    def test_extension_badExtension(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extension('notExisting'),
            None)

    def test_extensionToName_stringExtension(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extensionToName('200'),
            'cesar')

    def test_extensionToName_intExtension(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extensionToName(200),
            'cesar')

    def test_properName_whenPresent(self):
        schedule = Scheduling("""\
            names:
              cesar: César
            """)
        self.assertEqual(
            schedule.properName('cesar'),
            u'César')

    def test_properName_missing_usesTitle(self):
        schedule = Scheduling("""\
            names:
              cesar: César
            """)
        self.assertEqual(
            schedule.properName('perico'),
            u'Perico')

    def test_properName_noNamesAtAll(self):
        schedule = Scheduling("""\
            otherkey:
            """)
        self.assertEqual(
            schedule.properName('perico'),
            u'Perico')

    def test_intervals(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            """)
        self.assertEqual(
            schedule.intervals(), [
            '09:00-10:15',
            ])

    def test_intervals_withMoreThanTwo(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.intervals(), [
            '09:00-10:15',
            '10:15-11:30',
            ])


unittest.TestCase.__str__ = unittest.TestCase.id

# vim: ts=4 sw=4 et
