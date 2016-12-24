# -*- coding: utf-8 -*-

from .pbxmockup import PbxMockup, weekday
import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns

class PbxMockup_Test(unittest.TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))

    def test_currentQueue_noConfiguration(self):
        pbx = PbxMockup()
        result = pbx.currentQueue()
        self.assertEqual(result, [])

    def test_currentQueue_oneSlot_oneTurn(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
                - eduard
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
                2:
                - eduard
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
                - eduard
            hores:
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

    def test_restore(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('cesar')
        pbx.restore('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_restore_afterDoublePause(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.pause('cesar')
        pbx.pause('cesar')
        pbx.restore('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_currentQueue_withListFormat(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
                - eduard
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hores:
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
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
            hores:
            - '00:00'
            - '00:01'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])

    @unittest.skip("CURRENT TEST TO PASS")
    def test_addLine(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
              -
                - cesar
                - eduard
            hores:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        pbx.addLine('david')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=True),
            ns( key='eduard', paused=False),
            ns( key='david', paused=False),
            ])


unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
