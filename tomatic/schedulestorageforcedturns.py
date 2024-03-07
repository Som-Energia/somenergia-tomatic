# -*- encoding: utf-8 -*-

import datetime
import glob
from pathlib import Path
from yamlns import namespace as ns
from consolemsg import step
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

class BadEdit(Exception): pass

class Storage(object):
    "Stores schedules by week into a folder"

    def __init__(self, dirname=None):
        if not dirname and dbconfig:
            dirname = dbconfig.tomatic.get('forcedturnspath')
        if not dirname:
            packagedir = Path(__file__).parent
            dirname = packagedir/'..'/'data'
        self._dirname = Path(dirname)

    def _timetableFile(self):
        return self._dirname / 'forced-turns.yaml'

    @property
    def backupdir(self):
        return self._dirname/'backups'

    def createEmptyFile(self):
        emptytimetable = {}
        emptytimetable['days'] = 'dl dm dx dj dv'.split(' ')
        emptytimetable['turns'] = ['L1']
        emptytimetable['hours'] = ['09:00','10:15','11:30','12:45','14:00']
        emptytimetable['timetable'] = {'dl': [[None]], 'dm': [[None]], 'dx': [[None]], 'dj': [[None]], 'dv': [[None]]}
        timetable = ns(**emptytimetable)
        self.save(timetable)

    def load(self):
        filename = self._timetableFile()
        if not filename.is_file():
            self.createEmptyFile()

        try:
            return ns.load(str(filename))
        except IOError:
            raise KeyError(filename)

    def save(self, value):
        filename = self._timetableFile()
        value.dump(str(filename))

    def editSlot(self, day: str, houri: int, turni: int, name, user: str):
        timetable = self.load()
        # TODO: Ensure day, houri, turni and name are in timetable
        oldName = timetable.timetable[day][int(houri)][int(turni)]
        timetable.timetable[day][int(houri)][int(turni)] = name
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

    def addColumn(self):
        timetable = self.load()
        numberOfTurns = len(timetable.turns) + 1
        timetable.turns.append('L'+ str(numberOfTurns))
        for day in timetable.timetable:
            for hour in timetable.timetable[day]:
                hour.append(None)
        self.save(timetable)

    def removeColumn(self):
        timetable = self.load()

        def columnCanBeRemoved():
            canRemove = True
            for day in timetable.timetable:
                for hour in timetable.timetable[day]:
                    if (hour[-1] != None and hour[-1] != 'ningu'):
                        canRemove = False
            return canRemove

        if columnCanBeRemoved():
            timetable.turns.pop()
            for day in timetable.timetable:
                for hour in timetable.timetable[day]:
                    hour.pop()
        else:
            raise BadEdit("No es pot esborrar la columna perquè conté assignacions.")
        self.save(timetable)

#vim: ts=4 sw=4 et
