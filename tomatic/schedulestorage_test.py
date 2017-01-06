# -*- encoding: utf-8 -*-
import unittest
from . import schedulestorage
from yamlns import namespace as ns
import os

yaml20121110 = "week: '2012-11-10'"
yaml20030201 = "week: '2003-02-01'"

class ScheduleStorage_Test(unittest.TestCase):
    
    def setUp(self):
        import os
        self.storagedir = "deleteme"
        self.cleanUp()

        os.makedirs(self.storagedir)
        self.storage = schedulestorage.Storage(self.storagedir)

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        import shutil
        try:
            shutil.rmtree(self.storagedir)
        except: pass

    def write(self, filename, content):
        with open(os.path.join(self.storagedir, filename),'w') as f:
            f.write(content)

    def test_load(self):
        self.write('graella-2012-11-10.yaml', yaml20121110)

        data = self.storage.load("2012-11-10")
        self.assertEqual(data,ns.loads(yaml20121110))

    def test_load_missing(self):
        with self.assertRaises(KeyError) as ctx:
            data = self.storage.load("2000-01-02")

        self.assertEqual(str(ctx.exception),
            "'2000-01-02'")
 
    def test_load_notADate(self):
        with self.assertRaises(Exception) as ctx:
            data = self.storage.load("../../etc/passwd")

        self.assertEqual(str(ctx.exception),
            "time data '../../etc/passwd' does not match format '%Y-%m-%d'")
 
    def _test_load_notMonday(self): 'TODO'
    def _test_load_badFormat(self): 'TODO'

    def test_save(self):
        self.storage.save(ns.loads(yaml20121110))
        data = self.storage.load("2012-11-10")
        self.assertEqual(data,ns.loads(yaml20121110))

    def _test_save_missingDate(self): 'TODO'
    def _test_save_badDateValue(self): 'TODO'
    def _test_save_overwriting(self): 'TODO'


    def test_list_whenEmpty(self):
        self.assertEqual(self.storage.list(),[
            ]
        )

    def test_list_withOne(self):
        self.storage.save(ns.loads(yaml20121110))
        self.assertEqual(self.storage.list(),[
            '2012-11-10',
            ]
        )

    def test_list_withMany(self):
        self.storage.save(ns.loads(yaml20121110))
        self.storage.save(ns.loads(yaml20030201))
        self.assertEqual(self.storage.list(),[
            '2003-02-01',
            '2012-11-10',
            ]
        )


# vim: ts=4 sw=4 et
