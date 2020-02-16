# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .pbxasterisk import PbxAsterisk
from .scheduling import weekday, weekstart
from .schedulestorage import Storage
import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns
import tempfile
import os

class PbxAsterisk_Test(unittest.TestCase):

    def setUp(self):
        self.now = now = datetime.now()
        self.today = weekday(now)
        self.monday = weekstart(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))
        self.path = tempfile.mkdtemp()

    def tearDown(self):
        os.system('rm -rf {}'.format(self.path))

    def pbx(self):
        return PbxAsterisk(self.path, 'sqlite', 'demo.sqlite', create_db=True)

    def setupScheduling(self, yaml):
        sched = ns.loads(yaml)
        storage = Storage(self.path)
        sched.week = format(self.monday.date())
        storage.save(sched)

    def test_currentQueue_noConfiguration(self):
        pbx = self.pbx()
        result = pbx.currentQueue()
        self.assertEqual(result, [])

    def test_currentQueue_oneSlot_oneTurn(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_currentQueue_oneSlot_twoTurns(self):
        self.setupScheduling(u"""\
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
              eduard: 201
            """.format(
                today=self.today
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_twoTimes(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_beforeTime(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_currentQueue_afterTime(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ])


    def test_pause_withOne(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        pbx.pause('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=True),
            ])

    def test_pause_withTwoLines(self):
        self.setupScheduling(u"""\
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
              eduard: 201
            """.format(
                today=self.today
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        pbx.pause('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=True),
            ns( key='eduard', paused=False),
            ])

    def test_resume(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        pbx.pause('cesar')
        pbx.resume('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_resume_afterDoublePause(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        pbx.pause('cesar')
        pbx.pause('cesar')
        pbx.resume('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_currentQueue_withKeyFormat(self):
        self.setupScheduling(u"""\
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
              eduard: 201
            """.format(
                today=self.today
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_beforeTime_listFormat(self):
        self.setupScheduling(u"""\
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
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_currentQueue_afterTime_listFormat(self):
        pbx = self.pbx()
        self.setupScheduling(u"""\
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
            ))
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_addLine(self):
        self.setupScheduling(u"""\
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
              eduard: 201
              david: 202
            """.format(
                today=self.today
            ))
        pbx = self.pbx()
        pbx.setSchedQueue(self.now)
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
