# -*- encoding: utf-8 -*-
import unittest
from . import schedulestorage
from yamlns import namespace as ns
import os
from pathlib2 import Path

yaml20121112 = "week: '2012-11-12'"
yaml20030203 = "week: '2003-02-03'"
StorageError = schedulestorage.StorageError

class ScheduleStorage_Test(unittest.TestCase):

    from yamlns.testutils import assertNsEqual
    
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
        self.write('graella-2012-11-12.yaml', yaml20121112)

        data = self.storage.load("2012-11-12")
        self.assertEqual(data,ns.loads(yaml20121112))

    def test_load_badFormat(self):
        self.write('graella-2012-11-12.yaml', "\ttabs are not yaml")

        import yaml
        with self.assertRaises(yaml.error.YAMLError) as ctx:
            self.storage.load("2012-11-12")

    def test_load_missing(self):
        with self.assertRaises(KeyError) as ctx:
            self.storage.load("2000-01-03")

        self.assertEqual(str(ctx.exception),
            "'2000-01-03'")
 
    def test_load_notADate(self):
        with self.assertRaises(StorageError) as ctx:
            self.storage.load("../../etc/passwd")

        self.assertEqual(str(ctx.exception),
            "time data '../../etc/passwd' does not match format '%Y-%m-%d'")
 
    def test_load_notMonday(self):
        with self.assertRaises(StorageError) as ctx:
            self.storage.load("2020-01-01") # not a monday

        self.assertEqual(str(ctx.exception),
            "2020-01-01 is not a monday but a wednesday")

    def test_save(self):
        self.storage.save(ns.loads(yaml20121112))
        data = self.storage.load("2012-11-12")
        self.assertEqual(data,ns.loads(yaml20121112))

    def test_save_notADate(self):
        with self.assertRaises(StorageError) as ctx:
            self.storage.save(ns(week='../../etc/passwd'))
        self.assertEqual(format(ctx.exception),
            "time data '../../etc/passwd' does not match format '%Y-%m-%d'")

    def test_save_noWeekAttribute(self):
        with self.assertRaises(AttributeError) as ctx:
            self.storage.save(ns())
        self.assertEqual(format(ctx.exception),
            "week")

    def test_list_whenEmpty(self):
        self.assertEqual(self.storage.list(),[
            ]
        )

    def test_list_withOne(self):
        self.storage.save(ns.loads(yaml20121112))
        self.assertEqual(self.storage.list(),[
            '2012-11-12',
            ]
        )

    def test_list_withMany(self):
        self.storage.save(ns.loads(yaml20121112))
        self.storage.save(ns.loads(yaml20030203))
        self.assertEqual(self.storage.list(),[
            '2003-02-03',
            '2012-11-12',
            ]
        )

    def test_credit_noFiles(self):
        newCredit = self.storage.credit('2020-01-27')
        self.assertNsEqual(newCredit, """\
            {}
        """)

    def test_credit_withCreditSameDate(self):
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

    def test_credit_checksIsMonday(self):
        with self.assertRaises(StorageError) as ctx:
            self.storage.credit('2020-01-10')
        self.assertEqual(format(ctx.exception),
            "2020-01-10 is not a monday but a friday")

    def test_saveCredit_checksIsMonday(self):
        with self.assertRaises(StorageError) as ctx:
            self.storage.saveCredit('2020-01-10', ns(bob=5))

        self.assertEqual(format(ctx.exception),
            "2020-01-10 is not a monday but a friday")

    def assertContent(self, expected):
        self.assertNsEqual(ns(content=[
            str(x) for x in sorted(self.storage._dirname.glob('**/*'))
        ]), expected)

    def test_assertContent(self):
        self.storage.save(ns(week='2020-01-13'))
        self.storage.saveCredit('2020-01-06', ns(
            alice=2,
            bob=7,
        ))
        self.assertContent("""
            content:
            - deleteme/graella-2020-01-13.yaml
            - deleteme/shiftcredit-2020-01-06.yaml
        """)

    def test_retireOld(self):
        self.storage.save(ns(
            week='2020-01-06',
            overload = ns(bob=1),
        ))
        self.storage.save(ns(
            week='2020-01-13',
            overload = ns(bob=5),
        ))
        self.storage.save(ns(
            week='2020-01-20',
            overload = ns(bob=7),
        ))
        self.storage.saveCredit('2020-01-06', ns(
            alice=10,
            bob=20,
        ))

        self.storage.retireOld('2020-01-13')

        self.assertContent("""
            content:
            - deleteme/graella-2020-01-20.yaml
            - deleteme/old
            - deleteme/old/graella-2020-01-06.yaml
            - deleteme/old/graella-2020-01-13.yaml
            - deleteme/old/shiftcredit-2020-01-06.yaml
            - deleteme/shiftcredit-2020-01-13.yaml
        """)
        creditContent = Path('deleteme/shiftcredit-2020-01-13.yaml').read_text()
        self.assertNsEqual(creditContent, """
            alice: 10
            bob: 25
        """)




# TODO: Callers should consider credit is from the previous week to be computed


# vim: ts=4 sw=4 et
