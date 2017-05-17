# -*- coding: utf-8 -*-

import unittest
from .dbasterisk import DbAsterisk
from pony.orm import db_session, rollback
import os

class DbAsterisk_Test(unittest.TestCase):

    def setUp(self):
        rollback()
        try: os.unlink('tomatic/demo.sqlite')
        except: pass
        self.a = DbAsterisk("sqlite", 'demo.sqlite', create_db=True)
        db_session.__enter__()

    def tearDown(self):
        rollback()
        db_session.__exit__()
        try: os.unlink('tomatic/demo.sqlite')
        except: pass

    def fixture(self):
        return self.a

    def test_setQueue(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('202', False),
        ])

    def test_setQueue_overwrites(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('202', False),
        ])
        a.setQueue('aqueue',['400', '404', '402' ])
        self.assertEqual(a.queue('aqueue'), [
            ('400', False),
            ('404', False),
            ('402', False),
        ])

    def test_setQueue_emptyClears(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('202', False),
        ])
        a.setQueue('aqueue',[])
        self.assertEqual(a.queue('aqueue'), [
        ])

    def test_pause_anActiveMember(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        a.pause('aqueue','204')
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', True),
            ('202', False),
        ])
        
    def test_pause_missingExtension(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        a.pause('aqueue','bad')
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('202', False),
        ])

    def test_resume(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        a.pause('aqueue','204')
        a.resume('aqueue','204')
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('202', False),
        ])

    def test_add(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204'])
        a.add('aqueue', '400')
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('400', False),
        ])

    def test_setQueue_leavesOtherQueuesAlone(self):
        a = self.fixture()
        a.setQueue('aqueue',['200', '204', '202' ])
        a.setQueue('otherqueue',['400', '404', '402' ])
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
            ('204', False),
            ('202', False),
        ])

    def test_pause_leavesOtherQueuesAlone(self):
        a = self.fixture()
        a.setQueue('aqueue',['200'])
        a.setQueue('otherqueue',['200' ])
        a.pause('otherqueue', '200')
        self.assertEqual(a.queue('aqueue'), [
            ('200', False),
        ])
        self.assertEqual(a.queue('otherqueue'), [
            ('200', True),
        ])

    def test_resume_leavesOtherQueuesAlone(self):
        a = self.fixture()
        a.setQueue('aqueue',['200'])
        a.setQueue('otherqueue',['200' ])
        a.pause('aqueue', '200')
        a.pause('otherqueue', '200')
        a.resume('otherqueue', '200')
        self.assertEqual(a.queue('aqueue'), [
            ('200', True),
        ])
        self.assertEqual(a.queue('otherqueue'), [
            ('200', False),
        ])
        

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
