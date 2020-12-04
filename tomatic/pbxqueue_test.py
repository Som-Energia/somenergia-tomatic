# -*- coding: utf-8 -*-

import unittest
from yamlns import namespace as ns
from pathlib2 import Path

from . import pbxqueue
from . import persons

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
            pbxqueue.extract("strip([0-9]+)", "un 55 strip3333 numero"),
            "3333")

    def test_extractQueuepeerInfo_base(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base()
        )
 
    def test_extractQueuepeerInfo_notFound_usingExtensionAsNameAndKey(self):
        persons.persons.cache.extensions = ns()
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                key = '3063',
                name = '3063',
        ))

    def test_extractQueuepeerInfo_noSpecialName_titledKeyAsName(self):
        persons.persons.cache.names = ns()
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                name = 'Perico',
        ))

    def test_extractQueuepeerInfo_paused(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (paused) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                paused = True,
        ))
 
    def test_extractQueuepeerInfo_unavailable(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (Unavailable) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                disconnected = True,
        ))
 
    def test_extractQueuepeerInfo_busy(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (In use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                available = False,
        ))

    def test_extractQueuepeerInfo_incall(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (In use) (in call) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                available = False,
                incall = True,
        ))

    def test_extractqueuepeerinfo_unexpectedflags(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (unexpected) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                flags = ['unexpected']
        ))

    def test_extractqueuepeerinfo_ringing(self):
        line = "      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Ringing) (In use) has taken 6 calls (last was 181 secs ago)"
        self.assertNsEqual(
            pbxqueue.extractQueuepeerInfo(line),
            self.base(
                available = False,
                ringing = True,
        ))



unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
