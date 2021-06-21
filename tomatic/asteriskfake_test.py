# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from . import persons
from .asteriskfake import AsteriskFake


class AsteriskFake_Test(unittest.TestCase):

    from yamlns.testutils import assertNsEqual
    def setUp(self):
        self.persons = Path('p.yaml')

        self.persons.write_text(u"""\
            extensions:
              alice: '200'
              bob: '202'
              carol: '204'
              diana: '400'
              eva: '402'
              fanny: '404'
        """)
        ps = persons.persons(self.persons)
        self.a = self.setupPbx()

    def tearDown(self):
        self.tearDownPbx()
        persons.persons(False) # reset
        self.persons.unlink()

    def setupPbx(self):
        return AsteriskFake()

    def tearDownPbx(self):
        pass
    def fixture(self):
        return self.a

    def assertNames(self, result, expected):
        self.assertEqual([
            member.key
            for member in result
            ], expected)

    def assertPaused(self, result, expected):
        self.assertEqual([
            (member.key, member.paused)
            for member in result
            ], expected)

    def assertExtensions(self, result, expected):
        self.assertEqual([
            (member.key, member.extension)
            for member in result
            ], expected)

    def test_setQueue(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        self.assertNames(a.queue('aqueue'), [
            'alice',
            'carol',
            'bob',
        ])

    def test_queue_extensions(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        self.assertExtensions(a.queue('aqueue'), [
            ('alice', '200'),
            ('carol', '204'),
            ('bob', '202'),
        ])

    def test_setQueue_ignoresOutsiders(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'intruder' ])
        self.assertNames(a.queue('aqueue'), [
            'alice',
            'carol',
        ])


    def test_setQueue_overwrites(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice'])
        a.setQueue('aqueue',['carol', 'bob' ])
        self.assertNames(a.queue('aqueue'), [
            'carol',
            'bob',
        ])

    def test_setQueue_emptyClears(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        a.setQueue('aqueue',[])
        self.assertNames(a.queue('aqueue'), [
        ])

    def test_add(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol'])
        a.add('aqueue', 'diana')
        self.assertNames(a.queue('aqueue'), [
            'alice',
            'carol',
            'diana',
        ])

    def test_add_ignoresIntruder(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol'])
        a.add('aqueue', 'intruder')
        self.assertNames(a.queue('aqueue'), [
            'alice',
            'carol',
        ])

    def test_pause_defaultFalse(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        self.assertPaused(a.queue('aqueue'), [
            ('alice', False),
            ('carol', False),
            ('bob', False),
        ])
 
    def test_pause_anActiveMember(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        a.pause('aqueue','carol')
        self.assertPaused(a.queue('aqueue'), [
            ('alice', False),
            ('carol', True),
            ('bob', False),
        ])
        
    def test_pause_notInQueue_ignored(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol' ])
        a.pause('aqueue','bob')
        self.assertPaused(a.queue('aqueue'), [
            ('alice', False),
            ('carol', False),
        ])

    def test_pause_intruder_ignored(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        a.pause('aqueue','intruder')
        self.assertPaused(a.queue('aqueue'), [
            ('alice', False),
            ('carol', False),
            ('bob', False),
        ])

    def test_resume(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        a.pause('aqueue','carol')
        a.resume('aqueue','carol')
        self.assertPaused(a.queue('aqueue'), [
            ('alice', False),
            ('carol', False),
            ('bob', False),
        ])

    def test_setQueue_leavesOtherQueuesAlone(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice', 'carol', 'bob' ])
        a.setQueue('otherqueue',['diana', 'fanny', 'eva' ])
        self.assertNames(a.queue('aqueue'), [
            'alice',
            'carol',
            'bob',
        ])

    def test_pause_leavesOtherQueuesAlone(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice'])
        a.setQueue('otherqueue',['alice' ])
        a.pause('otherqueue', 'alice')
        self.assertPaused(a.queue('aqueue'), [
            ('alice', False),
        ])
        self.assertPaused(a.queue('otherqueue'), [
            ('alice', True),
        ])

    def test_resume_leavesOtherQueuesAlone(self):
        a = self.fixture()
        a.setQueue('aqueue',['alice'])
        a.setQueue('otherqueue',['alice' ])
        a.pause('aqueue', 'alice')
        a.pause('otherqueue', 'alice')
        a.resume('otherqueue', 'alice')
        self.assertPaused(a.queue('aqueue'), [
            ('alice', True),
        ])
        self.assertPaused(a.queue('otherqueue'), [
            ('alice', False),
        ])

    # Extensions

    def test_extensions_empty(self):
        a = self.fixture()
        self.assertEqual(a.extensions(), [
        ])
 
    def test_extensions_withOne(self):
        a = self.fixture()
        a.addExtension('201', 'Perico Palotes')
        self.assertEqual(a.extensions(), [
            ('201','Perico Palotes <201>'),
        ])
 
    def test_extensions_withMany(self):
        a = self.fixture()
        a.addExtension('201', 'Perico Palotes')
        a.addExtension('202', 'Juana Calamidad')
        self.assertEqual(a.extensions(), [
            ('201','Perico Palotes <201>'),
            ('202','Juana Calamidad <202>'),
        ])
 

    def test_clearExtensions(self):
        a = self.fixture()
        a.addExtension('201', 'Perico Palotes')
        a.clearExtensions()
        self.assertEqual(a.extensions(), [
        ])
 
    def test_removeExtensions(self):
        a = self.fixture()
        a.addExtension('201', 'Perico Palotes')
        a.addExtension('202', 'Juana Calamidad')
        a.removeExtension('201')
        self.assertEqual(a.extensions(), [
            ('202','Juana Calamidad <202>'),
        ])
 


# vim: ts=4 sw=4 et
