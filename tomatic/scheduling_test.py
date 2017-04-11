#!/usr/bin/env python
# -*- utf8 -*-

from .pbxmockup import weekday
import unittest
import pbxmysqlasterisk
from datetime import datetime, timedelta
from yamlns import namespace as ns
from scheduling import peekQueue

class Scheduling_Test(unittest.TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))

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

        



# vim: ts=4 sw=4 et

