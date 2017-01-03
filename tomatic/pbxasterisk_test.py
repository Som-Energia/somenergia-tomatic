# -*- coding: utf-8 -*-

from .pbxasterisk import Pbx, weekday, remotewrite, remoteread, remoterun
import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns

config=None
try:
    import config
except ImportError:
    pass

class RemoteFiles_Test(unittest.TestCase):

    def test_remoterun(self):
        result = remoterun(
            config.pbx.scp.username,
            config.pbx.scp.pbxhost,
            "cat /etc/hosts")
        self.assertIn('localhost', result)

    def test_remoteread(self):
        content = remoteread(
            config.pbx.scp.username,
            config.pbx.scp.pbxhost,
            "/etc/hosts")
        self.assertIn("localhost", content)

    def test_remoteread_badPath(self):
        with self.assertRaises(IOError) as ctx:
            content = remoteread(
                config.pbx.scp.username,
                config.pbx.scp.pbxhost,
                "/etc/badfile")
        self.assertEqual(str(ctx.exception),
            "[Errno 2] No such file")

    def test_remotewrite(self):
        try:
            content = "Some content"
            remotewrite(
                config.pbx.scp.username,
                config.pbx.scp.pbxhost,
                "borrame",
                content)
            result = remoteread(
                config.pbx.scp.username,
                config.pbx.scp.pbxhost,
                "borrame")
            self.assertEqual(result, content)
        finally:
            remoterun(
                config.pbx.scp.username,
                config.pbx.scp.pbxhost,
                'rm borrame'
                )
            


class Pbx_Test(unittest.TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))

    def pbx(self):
        return Pbx()

    def test_currentQueue_noConfiguration(self):
        pbx = self.pbx()
        result = pbx.currentQueue()
        self.assertEqual(result, [])

    @unittest.skip("Not yet implemented")
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
