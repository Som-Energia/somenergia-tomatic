#!/usr/bin/env python
# -*- coding: utf8 -*-

from .pbxmockup import weekday
import unittest
from datetime import datetime, timedelta, time
from yamlns.dateutils import Date
from scheduling import weekstart, nextweek, choosers, Scheduling

class Scheduling_Test(unittest.TestCase):

    def setUp(self):
        ''

    # weekday

    def test_weekday_withSunday(self):
        self.assertEqual(
            'dg', weekday(Date("2017-10-01")))

    def test_weekday_withMonday(self):
        self.assertEqual(
            'dl', weekday(Date("2017-10-02")))

    def test_weekday_withWenesday(self):
        self.assertEqual(
            'dx', weekday(Date("2017-10-04")))

    # weekstart

    def test_weekstart_withMonday(self):
        self.assertEqual(
            weekstart(Date("2017-10-02")),
            Date("2017-10-02"))

    def test_weekstart_withFriday(self):
        self.assertEqual(
            weekstart(Date("2017-10-06")),
            Date("2017-10-02"))

    # nextweek

    def test_nextweek_withMonday(self):
        self.assertEqual(
            nextweek(Date("2017-10-02")),
            Date("2017-10-09"))

    def test_nextweek_withFriday(self):
        self.assertEqual(
            nextweek(Date("2017-10-06")),
            Date("2017-10-09"))

    # extension

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

    # extensionToName

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

    # properName

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

    # intervals

    def test_intervals_withOneDate_notEnough(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            """)
        self.assertEqual(
            schedule.intervals(), [
            ])

    def test_intervals_withTwoDates(self):
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

    # peekInterval

    def test_peekInterval_beforeAnyInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("08:59"),None)

    def test_peekInterval_justInFirstInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("09:00"),0)

    def test_peekInterval_justBeforeNextInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("10:14"),0)

    def test_peekInterval_justInNextInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("10:15"),1)

    def test_peekInterval_justAtTheEndOfLastInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("11:29"),1)

    def test_peekInterval_pastLastInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("11:30"),None)

    def test_peekInterval_withNoHours(self):
        schedule = Scheduling("""\
            other:
            """)
        with self.assertRaises(Exception) as ctx:
            schedule.peekInterval("11:30")
        self.assertEqual(str(ctx.exception),
            "Schedule with no hours attribute")

    # choosers

    def test_choosers(self):
        now = datetime(2017,10,20,15,25,35)
        self.assertEqual(
            choosers(now),
            ("2017-10-16", 'dv', "15:25"))

    # peekQueue

    def test_peekQueue_oneSlot_oneTurn(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'cesar',
            ])

    def test_peekQueue_oneSlot_twoTurns(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'cesar',
            'eduard',
            ])

    def test_peekQueue_twoTimes(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'eduard',
            ])

    def test_peekQueue_beforeTime(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dl', '12:00'), [
            ])

    def test_peekQueue_afterTime(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            ])

    def test_peekQueue_nonExistingDay(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            ])

    def test_peekQueue_aDifferentDay(self):
        schedule = Scheduling(u"""\
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
        self.assertEqual(schedule.peekQueue('dm','12:00'), [
            'cesar',
            ])

    @unittest.skip("TODO")
    def test_peekQueue_withNobodySlots(self): pass


unittest.TestCase.__str__ = unittest.TestCase.id

# vim: ts=4 sw=4 et
