# -*- encoding: utf-8 -*-
import unittest
import datetime
import sys
from yamlns import namespace as ns
from pathlib import Path
from . import schedulestorage
from unittest.mock import patch
import contextlib

yaml20121112 = u"week: '2012-11-12'"
yaml20030203 = u"week: '2003-02-03'"

def timestamp(strdate):
    return datetime.datetime.strptime(
        strdate,
        "%Y-%m-%d %H:%M"
        )

@contextlib.contextmanager
def dbconfigFaker(content):
    """
    Reloads teh schedulestorage emulating a fake dbconfig
    with `content` as the `tomatic` attribute
    """
    try:
        with patch.dict('sys.modules', dbconfig=type(sys)('dbconfig')):
            from . import dbconfig
            dbconfig.tomatic=content
            import importlib
            importlib.reload(schedulestorage)
            yield
    finally:
        importlib.reload(schedulestorage)


class ScheduleStorage_Test(unittest.TestCase):

    from yamlns.testutils import assertNsEqual

    def setUp(self):
        self.storagedir = Path("deleteme")
        self.cleanUp()

        self.storagedir.mkdir(exist_ok=True)
        self.storage = schedulestorage.Storage(self.storagedir)

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        for p in reversed(sorted(self.storagedir.glob('**/*'))):
            p.rmdir() if p.is_dir() else p.unlink()

        if self.storagedir.exists():
            self.storagedir.rmdir()

    def write(self, filename, content):
        (self.storagedir/filename).write_text(content, encoding='utf8')

    def test_default_withDbConfig(self):
        with dbconfigFaker(ns(storagepath='mydir')):
            storage = schedulestorage.Storage()
            self.assertEqual(
                storage.backupdir.parent,
                Path('mydir')
            )

    def test_default_withoutDbConfig(self):
        with dbconfigFaker(ns()):
            storage = schedulestorage.Storage()
            self.assertEqual(
                storage.backupdir.parent,
                Path(__file__).parent/'../graelles'
            )

    def test_load(self):
        self.write('graella-2012-11-12.yaml', yaml20121112)

        data = self.storage.load("2012-11-12")
        self.assertEqual(data,ns.loads(yaml20121112))

    def test_load_badFormat(self):
        self.write('graella-2012-11-12.yaml', u"\ttabs are not yaml")

        import yaml
        with self.assertRaises(yaml.error.YAMLError) as ctx:
            self.storage.load("2012-11-12")

    def test_load_missing(self):
        with self.assertRaises(KeyError) as ctx:
            self.storage.load("2000-01-03")

        self.assertEqual(str(ctx.exception),
            "'2000-01-03'")
 
    def test_load_notADate(self):
        with self.assertRaises(schedulestorage.StorageError) as ctx:
            self.storage.load("../../etc/passwd")

        self.assertEqual(str(ctx.exception),
            "time data '../../etc/passwd' does not match format '%Y-%m-%d'")
 
    def test_load_notMonday(self):
        with self.assertRaises(schedulestorage.StorageError) as ctx:
            self.storage.load("2020-01-01") # not a monday

        self.assertEqual(str(ctx.exception),
            "2020-01-01 is not a monday but a wednesday")

    def test_save(self):
        self.storage.save(ns.loads(yaml20121112))
        data = self.storage.load("2012-11-12")
        self.assertEqual(data,ns.loads(yaml20121112))

    def test_save_notADate(self):
        with self.assertRaises(schedulestorage.StorageError) as ctx:
            self.storage.save(ns(week='../../etc/passwd'))
        self.assertEqual(format(ctx.exception),
            "time data '../../etc/passwd' does not match format '%Y-%m-%d'")

    def test_save_noWeekAttribute(self):
        with self.assertRaises(AttributeError) as ctx:
            self.storage.save(ns())
        self.assertEqual(format(ctx.exception),
            "week")

    def test_save_overExistingOne(self):
        timetable = ns.loads(yaml20121112)
        self.storage.save(timetable)
        timetable.modified = True
        self.storage.save(timetable)

        data = self.storage.load("2012-11-12")
        self.assertEqual(data,timetable)
        backups = list(Path('deleteme/backups').glob('*'))
        self.assertEqual(1, len(backups))
        backup = backups[0]
        self.assertRegex(
            backup.name,
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00-graella-2012-11-12.yaml$',
            )
        self.assertNsEqual(yaml20121112, ns.load(backup))

    def test_save_secondBackup(self):
        timetable = ns.loads(yaml20121112)
        self.storage.save(timetable)
        timetable.modified = True
        self.storage.save(timetable)
        timetable.remodified = True
        self.storage.save(timetable)

        backups = list(Path('deleteme/backups').glob('*'))
        self.assertEqual(2, len(backups))

    def test_backupRotate_withOldFile_removes(self):
        now = schedulestorage.utcnow()
        twoWeeksAgo = now - datetime.timedelta(days=14)
        oldFilename = twoWeeksAgo.isoformat()+'-graella-2012-11-12.yaml'
        self.storage.backupdir.mkdir()
        oldFile = self.storage.backupdir /oldFilename
        oldFile.touch()

        timetable = ns.loads(yaml20121112)
        self.storage.save(timetable)

        self.assertEqual(False, oldFile.exists())

    def test_backupRotate_withRecentFile_keeps(self):
        now = schedulestorage.utcnow()
        twoWeeksAgo = now - datetime.timedelta(days=13)
        oldFilename = twoWeeksAgo.isoformat()+'-graella-2012-11-12.yaml'
        self.storage.backupdir.mkdir()
        oldFile = self.storage.backupdir /oldFilename
        oldFile.touch()

        timetable = ns.loads(yaml20121112)
        self.storage.save(timetable)

        self.assertEqual(True, oldFile.exists())


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
        with self.assertRaises(schedulestorage.StorageError) as ctx:
            self.storage.credit('2020-01-10')
        self.assertEqual(format(ctx.exception),
            "2020-01-10 is not a monday but a friday")

    def test_saveCredit_checksIsMonday(self):
        with self.assertRaises(schedulestorage.StorageError) as ctx:
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


    def test_queueScheduledFor_matchingTimetable(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-06 09:40"))
        self.assertEqual(queue, ['first'])

    def test_queueScheduledFor_missingWeek(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-13 09:40"))
        self.assertEqual(queue, [])

    def test_queueScheduledFor_missingDoW(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-07 09:40"))
        self.assertEqual(queue, [])

    def test_queueScheduledFor_matchingTimetable(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-06 11:40"))
        self.assertEqual(queue, [])

    def test_queueScheduledFor_manyPersons(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
            - second
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-06 09:40"))
        self.assertEqual(queue, ['first','second'])

    def test_queueScheduledFor_choosesTime(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        - '11:00'
        timetable:
          dl:
          - - first
          - - second
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-06 10:40"))
        self.assertEqual(queue, ['second'])

    def test_queueScheduledFor_choosesDoW(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
          dm:
          - - second
        """))
        queue = self.storage.queueScheduledFor(timestamp("2020-01-07 09:40"))
        self.assertEqual(queue, ['second'])

    def test_calendar(self):
        self.storage.save(ns.loads("""\
        week: '2020-01-06'
        hours:
        - '09:00'
        - '10:00'
        timetable:
          dl:
          - - first
          dm:
          - - second
        """))
        calendar = self.storage.personIcs('first')
        nchars=320
        self.assertEqual(''.join(calendar)[:nchars],
            'BEGIN:VCALENDAR\r\n'
            'NAME:Atenció telèfon First\r\n'
            'X-WR-CALNAME:Atenció telèfon First\r\n'
            'X-PUBLISHED-TTL:PT1H\r\n'
            'VERSION:2.0\r\n'
            'PRODID:ics.py - http://git.io/lLljaA\r\n'
            'BEGIN:VEVENT\r\n'
            'BEGIN:VALARM\r\n'
            'ACTION:DISPLAY\r\n'
            'DESCRIPTION:\r\n'
            'TRIGGER:-PT15M\r\n'
            'END:VALARM\r\n'
            "DESCRIPTION:Torn d'atenció First\r\n"
            'DTEND:20200106T090000Z\r\n'
            'DTSTART:20200106T080000Z\r\n'
            'SUMMARY:Telèfon First\r\n'
            'UID:2020-01-06-dl-0-first@tomatic.somenergia.lan\r\n'
            'END:VEVENT\r\n'
            'END:VCALENDAR'[:nchars]
        )




# TODO: Callers should consider credit is from the previous week to be computed


# vim: ts=4 sw=4 et
