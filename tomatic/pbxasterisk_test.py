# -*- coding: utf-8 -*-

from .pbxasterisk import Pbx, remotewrite, remoteread, remoterun, Remote
from .scheduling import weekday
import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns

config=None
try:
    import config
except ImportError:
    pass


@unittest.skipIf(not config, "No config.py with pbx info")
class Pbx_Test(unittest.TestCase):

    def setUp(self):
        self.previousConfig = None
        self.remote = Remote(
            config.pbx.scp.username,
            config.pbx.scp.pbxhost,
            )
        self.previousConfig = self.remote.read(config.pbx.scp.path)
        self._pbx = Pbx(
            config.pbx.scp.username,
            config.pbx.scp.pbxhost,
            config.pbx.scp.path,
            **config.pbx['pbx']
            )
        self._pbx.reconfigure(ns.loads(u"""
            timetable: {}
            hours: []
            extensions: {}
            """))
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))

    def tearDown(self):
        if self.previousConfig is not None:
            print self.previousConfig
            self.remote.write(config.pbx.scp.path, self.previousConfig)

    def pbx(self):
        return self._pbx

    def test_currentQueue_noConfiguration(self):
        pbx = self.pbx()
        result = pbx.currentQueue()
        self.assertEqual(result, [])

    @unittest.skip("CURRENT GOAL")
    def test_currentQueue_oneSlot_oneTurn(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
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

    @unittest.skip("Not yet implemented")
    def test_currentQueue_oneSlot_twoTurns(self):
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

    @unittest.skip("Not yet implemented")
    def test_currentQueue_twoTimes(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
                2:
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

    @unittest.skip("Not yet implemented")
    def test_currentQueue_beforeTime(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
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

    @unittest.skip("Not yet implemented")
    def test_currentQueue_afterTime(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
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


    @unittest.skip("Not yet implemented")
    def test_pause_withOne(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
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

    @unittest.skip("Not yet implemented")
    def test_pause_withTwoLines(self):
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
        pbx.pause('cesar')
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=True),
            ns( key='eduard', paused=False),
            ])

    @unittest.skip("Not yet implemented")
    def test_resume(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
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

    @unittest.skip("Not yet implemented")
    def test_resume_afterDoublePause(self):
        pbx = self.pbx()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
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

    @unittest.skip("Not yet implemented")
    def test_currentQueue_withListFormat(self):
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

    @unittest.skip("Not yet implemented")
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

    @unittest.skip("Not yet implemented")
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

    @unittest.skip("Not yet implemented")
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
