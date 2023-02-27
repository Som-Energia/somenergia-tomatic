# -*- encoding: utf-8 -*-

import datetime
import glob
from pathlib import Path
from yamlns import namespace as ns
from .shiftload import loadSum
from .scheduling import Scheduling, choosers
dbconfig=None
try:
    import dbconfig
except ImportError:
    pass

class BadEdit(Exception): pass

def utcnow():
	"Returns tz aware current datetime in UTC"
	# Py2 compatible version
	import pytz
	return datetime.datetime.now(tz=pytz.utc)
	# Py3 only version
	#return datetime.datetime.now(tz=datetime.timezone.utc)

def fillConfigurationInfo():
    return ns.load('config.yaml')
CONFIG = fillConfigurationInfo()

class StorageError(Exception): pass

class Storage(object):
    "Stores schedules by week into a folder"

    def __init__(self, dirname=None):
        if not dirname and dbconfig:
            dirname = dbconfig.tomatic.get('storagepath')
        if not dirname:
            packagedir = Path(__file__).parent
            dirname = packagedir/'..'/'graelles'
        self._dirname = Path(dirname)

    def _checkMonday(self, monday):
        try:
            date = datetime.datetime.strptime(monday,'%Y-%m-%d')
        except ValueError as e:
            raise StorageError(e)

        if not date.weekday(): return
        weekdays = "monday tuesday wednesday thursday friday saturday sunday".split()
        raise StorageError("{} is not a monday but a {}".format(
            monday,
            weekdays[date.weekday()]
            ))

    def _timetableFile(self, monday):
        return self._dirname / 'graella-{}.yaml'.format(monday)

    def _timetableFiles(self):
        return sorted(self._dirname.glob('graella-????-??-??.yaml'))

    def _yamldate(self, path):
        return path.stem[-len('yyyy-mm-dd'):]

    def _creditFile(self, monday):
        return self._dirname / 'shiftcredit-{}.yaml'.format(monday)

    def _creditFiles(self):
        return sorted(self._dirname.glob('shiftcredit-????-??-??.yaml'))

    @property
    def backupdir(self):
        return self._dirname/'backups'

    def load(self, week):
        self._checkMonday(week)
        filename = self._timetableFile(week)
        try:
            return ns.load(str(filename))
        except IOError:
            raise KeyError(week)

    def _backupIfExist(self, week):
        filename = self._timetableFile(week)
        if not filename.exists(): return

        self.backupdir.mkdir(exist_ok=True)
        backupfile = self.backupdir/'{}-{}'.format(
            utcnow().isoformat(),
            filename.name)
        backupfile.write_bytes(filename.read_bytes())

    def clearOldBackups(self):
        twoWeeksAgo = (utcnow() - datetime.timedelta(days=14)).isoformat()

        for backup in self.backupdir.glob('*'):
            if backup.name <= twoWeeksAgo:
                backup.unlink()

    def save(self, value):
        self._checkMonday(value.week)
        filename = self._timetableFile(value.week)
        self.clearOldBackups()
        self._backupIfExist(week=value.week) 
        value.dump(str(filename))


    def list(self):
        return [
            self._yamldate(filename)
            for filename in self._timetableFiles()
            ]

    def credit(self, monday):
        """
        Returns the shift credit consisting on adding up the overloads
        in timetables up to the week of the specified monday, that week included.
        If a week has a precomputed shift credit, that is used instead of
        overloads of that week's timetable and earlier.
        """
        self._checkMonday(monday)
        currentCreditFile = self._creditFile(monday)
        filenames = [
            x for x in self._creditFiles()
            if x <= currentCreditFile
        ]
        creditFile = filenames[-1] if filenames else None

        credit = ns.load(str(creditFile)) if creditFile else ns()

        precomputedDate = self._yamldate(creditFile) if creditFile else '0000-00-00'
        lastTimetableToIgnore = self._timetableFile(precomputedDate)

        currentTimetable = self._timetableFile(monday)
        timetables = self._timetableFiles()
        overloads = (
            ns.load(str(timetable)).get('overload',ns())
            for timetable in timetables
            if timetable <= currentTimetable
            and timetable > lastTimetableToIgnore
        )

        return loadSum(credit, *overloads)


    def saveCredit(self, monday, credit):
        self._checkMonday(monday)
        filename = self._creditFile(monday)
        credit.dump(str(filename))

    def retireOld(self, monday):
        credit = self.credit(monday)

        retirementDir = self._dirname / 'old'
        if not retirementDir.exists():
            retirementDir.mkdir()

        currentCreditFile = self._creditFile(monday)
        for creditfile in self._creditFiles():
            if creditfile >= currentCreditFile: continue
            creditfile.rename(retirementDir/creditfile.name)

        currentTimetable = self._timetableFile(monday)
        for timetable in self._timetableFiles():
            if timetable > currentTimetable: continue
            timetable.rename(retirementDir/timetable.name)

        self.saveCredit(monday, credit)

    def editSlot(self, week: str, day: str, houri: int, turni: int, name, user: str):
        def occurrencesInTurn(timetable, day, houri, name):
            nominated = timetable.timetable[day][int(houri)]
            return nominated.count(name)

        timetable = self.load(week)
        # TODO: Ensure day, houri, turni and name are in timetable
        oldName = timetable.timetable[day][int(houri)][int(turni)]
        if name == 'ningu' and occurrencesInTurn(timetable, day, houri, name) == CONFIG.maxNingusPerTurn:
            raise BadEdit("Hi ha masses Ningu en aquest torn")
        timetable.timetable[day][int(houri)][int(turni)] = name
        timetable.overload = timetable.get('overload', ns())
        timetable.overload[oldName] = timetable.overload.get(oldName, 0) -1
        timetable.overload[name] = timetable.overload.get(name, 0) +1
        logmsg = (
            "{}: {} ha canviat {} {}-{} {} de {} a {}".format(
            utcnow(),
            user,
            day,
            timetable.hours[int(houri)],
            timetable.hours[int(houri)+1],
            timetable.turns[int(turni)],
            oldName,
            name
            ))
        step(logmsg)
        timetable.setdefault('log',[]).append(logmsg)
        self.save(timetable)
        publishStatic(timetable)

    def queueScheduledFor(self, timestamp):
        week, dow, time = choosers(timestamp)
        try: data = self.load(week)
        except KeyError: return []
        scheduling = Scheduling(data)
        return scheduling.peekQueue(dow, time)

    def personIcs(self, person):
        def constructDate(week, weekday, turn):
            monday = datetime.date.fromisoformat(week)
            date = addDays(monday, days.index(day))
            isoString = f"{date}T{times[turn]}:00"
            try:
                import zoneinfo
            except ImportError:
                from backports import zoneinfo
            tz = zoneinfo.ZoneInfo("Europe/Madrid")
            dt = datetime.datetime.strptime(isoString, "%Y-%m-%dT%H:%M:%S")
            return dt.replace(tzinfo=tz)

        from .retriever import addDays
        import ics
        calendar = ics.Calendar()
        for week in self.list():
            data = self.load(week)
            times = data.hours
            monday = datetime.date.fromisoformat(week)
            days='dl dm dx dj dv'.split()
            for day, turns in data.timetable.items():
                for turn, people in enumerate(turns):
                    if person not in people: continue
                    event = ics.Event(
                        name = "Telèfon",
                        uid = f"{week}-{day}-{turn}-{person}@tomatic.somenergia.lan",
                        begin = constructDate(week, day, turn),
                        end = constructDate(week, day, turn+1),
                        description="Torn d'atenció",
                    )
                    alarm = ics.DisplayAlarm(
                        trigger=datetime.timedelta(minutes=-15),
                    )
                    event.alarms.append(alarm)
                    calendar.events.add(event)
        return calendar

# TODO: Move anywhere
from .htmlgen import HtmlGen
from .remote import remotewrite
from consolemsg import step

def publishStatic(timetable):
    step("publishStatic")
    if not dbconfig: return
    step("publishStatic: dbconfig exists")
    if not hasattr(dbconfig, 'tomatic'): return
    step("publishStatic: tomatic exists")
    if not hasattr(dbconfig.tomatic, 'publishStatic'): return
    step("publishStatic: publishStatic exists {}", dbconfig.tomatic.publishStatic)
    params = dbconfig.tomatic.publishStatic
    sched=HtmlGen(timetable)
    params=ns(params,
        username = params.user,
        filename = str(Path(params.path) / 'graella-{week}.html'.format(**timetable)),
    )
    del params.user
    del params.path
    remotewrite(
        content = sched.html(),
        **params
    )

#vim: ts=4 sw=4 et
