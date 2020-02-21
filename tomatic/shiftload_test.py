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

    def _test_(self):
        lines = Path('indisponibilitats-vacances.conf').read_text(encoding='utf8').split('\n')
        vacances = busy.parseBusy(lines)
        self.assertNsEqual(ns(vacances=list(vacances)), """\
                vacances: 
                """)

    def test_workingDays(self):
        workingDays = shiftload.workingDays(
            person='alice',
            holidays=[],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withLeave(self):
        workingDays = shiftload.workingDays(
            person='alice',
            holidays=[],
            daysoff=[],
            leaves=['alice'],
        )
        self.assertEqual(workingDays,0)

    def test_workingDays_withOthersLeave(self):
        workingDays = shiftload.workingDays(
            person='alice',
            holidays=[],
            daysoff=[],
            leaves=['bob'],
        )
        self.assertEqual(workingDays,5)


    def test_ponderatedLoad_(self):
        ideal = ns(
            alice=60,
            bob=60,
        )
        load = shiftload.ponderatedLoad(ideal, 
            holidays=[],
            daysoff=[],
            leaves=[],
        )
        self.assertNsEqual(load, """\
            alice: 60
            bob: 60
        """)


# vim: et ts=4 sw=4
