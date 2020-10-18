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


from . import pbxasterisk
from . import persons
from pathlib2 import Path

class Parser_Test(unittest.TestCase):

    personfile = Path('p.yaml')
    from yamlns.testutils import assertNsEqual

    def setUp(self):
        self.setupPersons(u"""
            extensions:
                perico: '3063'
            names:
                perico: Palotes
        """)

    def base(self, **kwds):
        return ns(ns.loads(u"""\
            available: true
            disconnected: false
            ringing: false
            extension: '3063'
            flags: []
            incall: false
            key: perico
            name: Palotes
            ncalls: 6
            paused: false
            secondsSinceLastCall: 181
        """), **kwds)

    def setupPersons(self,content):
        self.personfile.write_text(content, encoding='utf8')
        persons.persons(self.personfile)

    def tearDown(self):
        if self.personfile.exists():
            self.personfile.unlink()
        

    def test_extract_notfound(self):
        self.assertEqual(
            pbxasterisk.extract("strip([0-9]+)", "un 55 strip3333 numero"),
            "3333")

    def test_extractQueuepeerInfo_base(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base()
        )
 
    def test_extractQueuepeerInfo_notFound_usingExtensionAsNameAndKey(self):
        persons.persons.cache.extensions = ns()
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                key = '3063',
                name = '3063',
        ))

    def test_extractQueuepeerInfo_noSpecialName_titledKeyAsName(self):
        persons.persons.cache.names = ns()
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                name = 'Perico',
        ))

    def test_extractQueuepeerInfo_paused(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (paused) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                paused = True,
        ))
 
    def test_extractQueuepeerInfo_unavailable(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (Unavailable) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                disconnected = True,
        ))
 
    def test_extractQueuepeerInfo_busy(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (In use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                available = False,
        ))

    def test_extractQueuepeerInfo_incall(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (In use) (in call) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                available = False,
                incall = True,
        ))

    def test_extractqueuepeerinfo_unexpectedflags(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (unexpected) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                flags = ['unexpected']
        ))

    def test_extractqueuepeerinfo_ringing(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Ringing) (In use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxasterisk.extractQueuepeerInfo(line),
            self.base(
                available = False,
                ringing = True,
        ))


unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
