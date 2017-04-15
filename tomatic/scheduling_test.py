#!/usr/bin/env python
# -*- utf8 -*-

from .pbxmockup import weekday
import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns
<<<<<<< c583ae7a17da0de5f93f41fbb602ee8607f4cc1a
from yamlns.dateutils import Date
from scheduling import peekQueue, weekstart, nextweek
=======
from scheduling import peekQueue, Scheduling
>>>>>>> Scheduling.extension,extensionToName

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

<<<<<<< c583ae7a17da0de5f93f41fbb602ee8607f4cc1a
    @unittest.skip("TODO")
    def test_peekQueue_withNobodySlots(self): "TODO"
=======
    def test_extension_existing(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extension('cesar'),
            '200')
>>>>>>> Scheduling.extension,extensionToName

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



<<<<<<< c583ae7a17da0de5f93f41fbb602ee8607f4cc1a
unittest.TestCase.__str__ = unittest.TestCase.id


=======


unittest.TestCase.__str__ = unittest.TestCase.id

>>>>>>> Scheduling.extension,extensionToName
# vim: ts=4 sw=4 et
