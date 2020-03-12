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
            self.storage.load("2000-01-02")

        self.assertEqual(str(ctx.exception),
            "'2000-01-02'")
 
    def test_load_notADate(self):
        with self.assertRaises(Exception) as ctx:
            self.storage.load("../../etc/passwd")

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

    def _test_toplevel_goal(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        self.storage.save(ns(week='2020-01-06',
            overload = ns(bob=7)
        ))
        self.storage.save(ns(week='2020-01-13'))
        newCredit = self.storage.credit('2020-01-27')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: 4
        """)

    from yamlns.testutils import assertNsEqual

    def test_toplevel_noFiles(self):
        newCredit = self.storage.credit('2020-01-27')
        self.assertNsEqual(newCredit, """\
            {}
        """)

    def test_toplevel_withCredit(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        newCredit = self.storage.credit('2020-01-06')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: -3
        """)

    def test_toplevel_withOlderCredit(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: -3
        """)


    def test_toplevel_withManyCredits_takesLastDate(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        self.storage.saveCredit('2020-01-13', ns(
            alice=20,
            bob=-30,
        ))
        newCredit = self.storage.credit('2020-01-20')
        self.assertNsEqual(newCredit, """\
            alice: 20
            bob: -30
        """)

    def test_toplevel_withManyCredits_ignoresFutureCredit(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        self.storage.saveCredit('2020-01-13', ns(
            alice=20,
            bob=-30,
        ))
        newCredit = self.storage.credit('2020-01-06')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: -3
        """)









# vim: ts=4 sw=4 et
