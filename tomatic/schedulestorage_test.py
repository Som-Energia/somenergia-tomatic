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

    def test_save_notADate(self):
        with self.assertRaises(Exception) as ctx:
            self.storage.save(ns(week='../../etc/passwd'))
        self.assertEqual(format(ctx.exception),
            "time data '../../etc/passwd' does not match format '%Y-%m-%d'")

    def test_save_missingDate(self):
        # TODO: a different error
        with self.assertRaises(AttributeError) as ctx:
            self.storage.save(ns())
        self.assertEqual(format(ctx.exception),
            "week")

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

    from yamlns.testutils import assertNsEqual

    def test_credit_noFiles(self):
        newCredit = self.storage.credit('2020-01-27')
        self.assertNsEqual(newCredit, """\
            {}
        """)

    def test_credit_withCredit(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        newCredit = self.storage.credit('2020-01-06')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: -3
        """)

    def test_credit_withOlderCredit(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=-3,
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: -3
        """)

    def test_credit_withManyCredits_takesLastDate(self):
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

    def test_credit_withManyCredits_ignoresFutureCredit(self):
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

    def test_credit_justFutureCredit_ignoresAll(self):
        self.storage.saveCredit('2020-01-13', ns(
            alice=2,
            bob=-3,
        ))
        newCredit = self.storage.credit('2020-01-06')
        self.assertNsEqual(newCredit, """\
            {}
        """)


    def test_credit_withTimetable(self):
        self.storage.save(ns(
            week='2020-01-13',
            overload = ns(bob=7),
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            bob: 7
        """)

    def test_credit_timetableWithoutOverload(self):
        self.storage.save(ns(
            week='2020-01-13',
        ))
        
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            {}
        """)

    def test_credit_manyTimetables(self):
        self.storage.save(ns(
            week='2020-01-06',
            overload = ns(alice=3, bob=-3),
        ))
        self.storage.save(ns(
            week='2020-01-13',
            overload = ns(bob=7),
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            alice: 3
            bob: 4
        """)

    def test_credit_creditAndTimetable_added(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=7,
        ))
        self.storage.save(ns(
            week='2020-01-13',
            overload = ns(alice=3, bob=-3),
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            alice: 5
            bob: 4
        """)

    def test_credit_futureTimetable_ignored(self):
        self.storage.save(ns(
            week='2020-01-13',
            overload = ns(alice=3, bob=-3),
        ))
        self.storage.save(ns(
            week='2020-01-20',
            overload = ns(bob=7),
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            alice: 3
            bob: -3
        """)

    def test_credit_oldTimetable_ignored(self):
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=7,
        ))
        self.storage.save(ns(
            week='2020-01-06',
            overload = ns(alice=3, bob=-3),
        ))
        newCredit = self.storage.credit('2020-01-13')
        self.assertNsEqual(newCredit, """\
            alice: 2
            bob: 7
        """)


# TODO: Check mondays are dates (not in private functions)
# TODO: Callers should consider credit is from the previous week to be computed


# vim: ts=4 sw=4 et
