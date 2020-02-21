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


    def test_ponderatedLoad_(self):
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
            alice: 60
            bob: 60
        """)


# vim: et ts=4 sw=4
