# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timedelta
from pathlib2 import Path
from yamlns import namespace as ns

from . import persons
from .pbxmockup import PbxMockup, weekday

class PbxMockup_Test(unittest.TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))
        self.persons = Path('p.yaml')

        self.persons.write_text(u"""\
            extensions:
              cesar: 200
        """)
        ps = persons.persons('p.yaml')

    def tearDown(self):
        persons.persons(False) # reset
        self.persons.unlink()

    def pbx(self):
        return PbxMockup()

    def test_currentQueue_noConfiguration(self):
        pbx = self.pbx()
        result = pbx.currentQueue()
        self.assertEqual(result, [])

    def test_currentQueue_oneSlot_oneTurn(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_currentQueue_oneSlot_twoTurns(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_twoTimes(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
              -
                - eduard
            hours:
            - '00:00'
            - '{splithour:02d}:00'
            - '23:59'

            extensions:
              cesar: 200
              eduard: 201
            """.format(
                splithour=self.currentHour,
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_beforeTime(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '23:58'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_currentQueue_afterTime(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '00:00'
            - '00:01'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])


    def test_pause_withOne(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=True),
            ])

    def test_pause_withTwoLines(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=True),
            ns( key='eduard', paused=False),
            ])

    def test_pause_unexistingLine(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('notexisting')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ns( key='eduard', paused=False),
            ])

    def test_resume(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('cesar')
        pbx.resume('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_resume_afterDoublePause(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('cesar')
        pbx.pause('cesar')
        pbx.resume('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_currentQueue_withKeyFormat(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_beforeTime_listFormat(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '23:58'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_currentQueue_afterTime_listFormat(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hours:
            - '00:00'
            - '00:01'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_addLine(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.addLine('david')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ns( key='eduard', paused=False),
            ns( key='david', paused=False),
            ])


unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
