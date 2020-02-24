#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest
from . import shiftload
from yamlns import namespace as ns
from . import busy
from pathlib2 import Path

class ShiftLoadTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff=None

    from yamlns.testutils import assertNsEqual

    def _test_commented(self):
        lines = Path('indisponibilitats-vacances.conf').read_text(encoding='utf8').split('\n')
        vacances = busy.parseBusy(lines)
        self.assertNsEqual(ns(vacances=list(vacances)), """\
                vacances: 
                """)

    def test_workingDays_allWorkingDays(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withLeave(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=['alice'],
        )
        self.assertEqual(workingDays,0)

    def test_workingDays_withOthersLeave(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=['bob'],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withOneDayoff(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[ns(
                optional = False,
                person = 'alice',
                reason = 'a reason',
                turns = '1111',
                weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_workingDays_withOneDayoffFromSomeOneElse(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'bob',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withManyDaysOff(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                ),
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dm',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,3)

    def test_workingDays_withOneHoliday(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_workingDays_withDayOffInHolidays(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_singlePonderatedLoad_withHolidays(self):
        load = shiftload.singlePonderatedLoad(
            person='alice',
            load=10,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(load, 8.0)

    def test_singlePonderatedLoad_withHolidaysAndDayOff(self):
        load = shiftload.singlePonderatedLoad(
            person='alice',
            load=10,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dm',
                )],
            leaves=[],
        )
        self.assertEqual(load, 6.0)

    def test_singlePonderatedLoad_withHolidaysAndLeaves(self):
        load = shiftload.singlePonderatedLoad(
            person='alice',
            load=10,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=['alice'],
        )
        self.assertEqual(load, 0.0)

    def test_ponderatedLoad_allWorkingDays(self):
        ideal = ns(
            alice=60,
            bob=60,
        )
        load = shiftload.ponderatedLoad(ideal, 
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertNsEqual(load, """\
            alice: 60.0
            bob: 60.0
        """)

    def test_ponderatedLoad_withHolidaysAndDayOff(self):
        ideal = ns(
            alice=10,
            bob=10,
        )
        load = shiftload.ponderatedLoad(ideal, 
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'bob',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dm',
                )],
            leaves=[],
        )
        self.assertNsEqual(load, """\
            alice: 8.0
            bob: 6.0
        """)

    def test_dayCapacity_noBusy(self):
        capacity = shiftload.dayCapacity(busy='0000',maxPerDay=2)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_allBusy(self):
        capacity = shiftload.dayCapacity(busy='1111',maxPerDay=2)
        self.assertEqual(capacity, 0)

    def test_dayCapacity_lastHalfDayBusy(self):
        capacity = shiftload.dayCapacity(busy='0011',maxPerDay=2)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_firstHalfDayBusy(self):
        capacity = shiftload.dayCapacity(busy='1100',maxPerDay=2)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_middleDayBusy(self):
        capacity = shiftload.dayCapacity(busy='0110',maxPerDay=2)
        self.assertEqual(capacity, 1)

    def test_dayCapacity_max1AndAvailable(self):
        capacity = shiftload.dayCapacity(busy='0011',maxPerDay=1)
        self.assertEqual(capacity, 1)

    def test_dayCapacity_max1AllBusy(self):
        capacity = shiftload.dayCapacity(busy='1111',maxPerDay=1)
        self.assertEqual(capacity, 0)

    def test_dayCapacity_max3_noBusy(self):
        capacity = shiftload.dayCapacity(busy='0000',maxPerDay=3)
        self.assertEqual(capacity, 3)

    def test_dayCapacity_max3_twoBusy(self):
        capacity = shiftload.dayCapacity(busy='1001',maxPerDay=3)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_max3_threeBusy(self):
        capacity = shiftload.dayCapacity(busy='1011',maxPerDay=3)
        self.assertEqual(capacity, 1)

    def test_weekCapacity(self):
        capacity = shiftload.weekCapacity(busy=[
            '0000',
            '0011',
            '1111',
            '0111',
            '1001',
        ], maxPerDay = 2)
        self.assertEqual(capacity, 2+2+0+1+1)

    def test_weekCapacity_max3(self):
        capacity = shiftload.weekCapacity(busy=[
            '0000',
            '0011',
            '1111',
            '0111',
            '1001',
        ], maxPerDay = 3)
        self.assertEqual(capacity, 3+2+0+1+2)

    def test_achieveFullLoad_alreadyComplete(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=2,
            limits = ns(
                alice=10,
                bob=10,
            ),
            debts = ns(
                alice=0,
                bob=0,
            ),
            shifts = ns(
                alice=1,
                bob=1,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 1
            bob: 1
        """)


# vim: et ts=4 sw=4
