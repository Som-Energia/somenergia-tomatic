# -*- encoding: utf-8 -*-

from yamlns import namespace as ns
import os
import datetime
import glob
from pathlib2 import Path

class Storage(object):
    "Stores schedules by week into a folder"

    def __init__(self, dirname):
        self._dirname = Path(dirname)

    def _filename(self, week):
        week = datetime.datetime.strptime(week,'%Y-%m-%d')
        return str(
            self._dirname / "graella-{:%Y-%m-%d}.yaml".format(week))

    def load(self, week):
        filename = self._filename(week)
        try:
            return ns.load(filename)
        except IOError:
            raise KeyError(week)

    def save(self, value):
        filename = self._filename(value.week)
        value.dump(filename)

    def list(self):
        return [
            filename.stem[-len('yyyy-mm-dd'):]
            for filename in sorted(self._dirname.glob('graella-*.yaml'))
            ]

    def credit(self, monday):
        currentTimetable = self._dirname / 'graella-{}.yaml'.format(monday)
        timetables = list(self._dirname.glob('graella-????-??-??.yaml'))

        from .shiftload import loadSum

        if timetables:
            return loadSum(*[
                ns.load(str(timetable)).get('overload',ns())
                for timetable in timetables
            ])

        current = self._dirname / 'shiftcredit-{}.yaml'.format(monday)
        filenames = list(sorted(
            x for x in self._dirname.glob('shiftcredit-????-??-??.yaml')
            if x <= current
            ))
        if not filenames: return ns()
        return ns.load(str(filenames[-1]))


    def saveCredit(self, monday, credit):
        filename = self._dirname / 'shiftcredit-{}.yaml'.format(monday)
        credit.dump(str(filename))





#vim: ts=4 sw=4 et
