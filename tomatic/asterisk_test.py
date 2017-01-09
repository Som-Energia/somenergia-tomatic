# -*- coding: utf-8 -*-

import asterisk
from Asterisk.Manager import Manager
import os
from .htmlgen import schedule2asterisk
from yamlns import namespace as ns

from remote import remoterun

config=None
try:
    import config
except ImportError:
    pass

import unittest

class Asterisk_Test(unittest.TestCase):

    def ns(self,content):
        return ns.loads(content)

    def tearDown(self):
        if config:
            sshconfig = config.pbx['scp']
            path = os.path.dirname(sshconfig['path'])
            file = os.path.basename(sshconfig['path'])
            remoterun(
                user = sshconfig['username'],
                host = sshconfig['pbxhost'],
                command = 'cd {}; git checkout {}'
                    .format(path, file))
            manager = Manager(**config.pbx['pbx'])
            manager.Command('reload')

    def setupPbx(self):
        return asterisk.Pbx(config.pbx)


    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskSend_oneTurnOneSip(self):
        asterisk_conf = schedule2asterisk(self.ns("""\
        timetable:
          dl:
            1:
            - ana
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        extensions:
          ana: 217
        week: '2016-07-25'
        """)
        )
        pbx = self.setupPbx()
        pbx.sendConfNow(asterisk_conf)
        queues = pbx.receiveConf()
        self.assertIn('entrada_cua_dl_1',queues)
        queue = queues['entrada_cua_dl_1']
        self.assertIn('members',queue)
        members = queue['members']
        self.assertIn('SIP/217',members)

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskSend_oneTurnManySip(self):
        schedule = self.ns("""\
            timetable:
              dl:
                1:
                - ana
                - jordi
                - pere
            hours:
            - '09:00'
            - '10:15'
            turns:
            - T1
            - T2
            - T3
            colors:
              pere: 8f928e
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 217
              jordi: 210
              pere: 224
            week: '2016-07-25'
            """)
        asterisk_conf = schedule2asterisk(schedule)
        pbx = self.setupPbx()
        pbx.sendConfNow(asterisk_conf)
        queues = pbx.receiveConf()
        self.assertIn('entrada_cua_dl_1',queues)
        queue = queues['entrada_cua_dl_1']
        self.assertIn('members',queue)
        members = queue['members']
        self.assertIn('SIP/217',members)
        self.assertIn('SIP/210',members)
        self.assertIn('SIP/224',members)

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskSend_manyTurnManySip(self):
        schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - jordi
            - pere
            2:
            - pere
            - jordi
          dm:
            1:
            - jordi
            - ana
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          jordi: 210
          pere: 224
        week: '2016-07-25'
        """)
        asterisk_conf = schedule2asterisk(schedule)
        pbx = self.setupPbx()
        pbx.sendConfNow(asterisk_conf)
        queues = pbx.receiveConf()
        self.assertIn('entrada_cua_dl_1',queues)
        queue = queues['entrada_cua_dl_1']
        self.assertIn('members',queue)
        members = queue['members']
        self.assertIn('SIP/217',members)
        self.assertIn('SIP/210',members)
        self.assertIn('SIP/224',members)
        self.assertIn('entrada_cua_dl_2',queues)
        queue = queues['entrada_cua_dl_2']
        self.assertIn('members',queue)
        members = queue['members']
        self.assertIn('SIP/210',members)
        self.assertIn('SIP/224',members)
        self.assertIn('entrada_cua_dm_1',queues)
        queue = queues['entrada_cua_dm_1']
        self.assertIn('members',queue)
        members = queue['members']
        self.assertIn('SIP/210',members)
        self.assertIn('SIP/217',members)

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskReceive_oneTurnManySip(self):
        schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """)
        asterisk_conf = schedule2asterisk(schedule)
        pbx = self.setupPbx()
        pbx.sendConfNow(asterisk_conf)
        h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
        h_asterisk_yaml = h_asterisk.getYaml()
        self.assertIn('timetable',h_asterisk_yaml)
        self.assertIn('dl',h_asterisk_yaml.timetable)
        self.assertIn(1,h_asterisk_yaml.timetable.dl)
        self.assertEqual(
            set(h_asterisk.getYaml().timetable.dl[1]),
            set(schedule.timetable.dl[1])
        )

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskReceive_manyTurnManySip(self):
       schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
          dm:
            1:
            - ana
            - pere
            - jordi
            2:
            - pere
            - jordi
            - ana
        hours:
        - '09:00'
        - '10:15'
        - '11:30'
        turns:
        - T1
        - T2
        - T3

        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """)
       asterisk_conf = schedule2asterisk(schedule)
       pbx = self.setupPbx()
       pbx.sendConfNow(asterisk_conf)
       h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('timetable',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.timetable)
       self.assertIn(1,h_asterisk_yaml.timetable.dl)
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dl[1]),
           set(schedule.timetable.dl[1])
       )
       self.assertIn('dm',h_asterisk_yaml.timetable)
       self.assertIn(1,h_asterisk_yaml.timetable.dm)
       self.assertIn(2,h_asterisk_yaml.timetable.dm)
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dm[1]),
           set(schedule.timetable.dm[1])
       )
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dm[2]),
           set(schedule.timetable.dm[2])
       )

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskPause_oneSipPaused(self):
       schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        extensions:
          ana: 217
        week: '2016-07-25'
        """)
       asterisk_conf = schedule2asterisk(schedule)
       pbx = self.setupPbx()
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],['ana'])

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskPause_manySipOnePaused(self):
       schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        - T2
        - T3
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """)
       asterisk_conf = schedule2asterisk(schedule)
       pbx = self.setupPbx()
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],['ana'])

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskResume_oneSipOneResumed(self):
       schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        extensions:
          ana: 217
        week: '2016-07-25'
        """)
       asterisk_conf = schedule2asterisk(schedule)
       pbx = self.setupPbx()
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       pbx.resume('dl',1,217)
       h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],[])

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskPause_OnePausedOneResumed(self):
       schedule = self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hours:
        - '09:00'
        - '10:15'
        turns:
        - T1
        - T2
        - T3
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """)
       asterisk_conf = schedule2asterisk(schedule)
       pbx = self.setupPbx()
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       pbx.pause('dl',1,218)
       pbx.resume('dl',1,217)
       h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],['pere'])

    @unittest.skipIf(not config, "depends on pbx")
    def test_parsePause_onePaused(self):
        schedule = self.ns("""\
            timetable:
              dl:
                1:
                - ana
                - pere
                - jordi
              dm:
                1:
                - ana
                - pere
                - jordi
            hours:
            - '09:00'
            - '10:15'
            turns:
            - T1
            - T2
            - T3
            extensions:
              ana: 217
              pere: 218
              jordi: 219
            week: '2016-07-25'
            """)
        difference = self.ns("""\
            dm:
              1:
                219: added
            """)
        asterisk_conf = schedule2asterisk(schedule)
        pbx = self.setupPbx()
        pbx.sendConfNow(asterisk_conf)
        pbx.parsePause(difference)
        h_asterisk = asterisk.HtmlGenFromAsterisk(schedule,pbx.receiveConf())
        h_asterisk_yaml = h_asterisk.getYaml()
        self.assertIn('paused',h_asterisk_yaml)
        self.assertIn('dm',h_asterisk_yaml.paused)
        self.assertIn(1,h_asterisk_yaml.paused.dm)
        self.assertEqual(h_asterisk_yaml.paused.dm[1],['jordi'])


# vim: ts=4 sw=4 et
