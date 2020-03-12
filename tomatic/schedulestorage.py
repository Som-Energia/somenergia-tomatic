# -*- encoding: utf-8 -*-

import os
import datetime
import glob
from pathlib2 import Path
from yamlns import namespace as ns
from .shiftload import loadSum

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

    def _creditFile(self, monday):
        return self._dirname / 'shiftcredit-{}.yaml'.format(monday)

    def _creditFiles(self):
        return sorted(self._dirname.glob('shiftcredit-????-??-??.yaml'))

    def _timetableFile(self, monday):
        return self._dirname / 'graella-{}.yaml'.format(monday)

    def _timetableFiles(self):
        return sorted(self._dirname.glob('graella-????-??-??.yaml'))

    def _yamldate(self, path):
        return str(path)[-len('yyyy-mm-dd.yaml'):-len('.yaml')]

    def credit(self, monday):
        """
        Returns the shift credit consisting on adding up the overloads
        in timetables up to the week of the specified monday, that week included.
        If a previous week has a precomputed shift credit, it uses that
        as base.
        """

        current = self._creditFile(monday)
        filenames = [
            x for x in self._creditFiles()
            if x <= current
        ]
        creditFile = filenames[-1] if filenames else None

        credit = ns.load(str(creditFile)) if creditFile else ns()

        ignoredDate = self._yamldate(creditFile) if creditFile else '0000-00-00'
        lastExcludedTimetable = self._timetableFile(ignoredDate)

        currentTimetable = self._timetableFile(monday)
        timetables = self._timetableFiles()
        overloads = (
            ns.load(str(timetable)).get('overload',ns())
            for timetable in timetables
            if timetable <= currentTimetable
            and timetable > lastExcludedTimetable
        )

        return loadSum(credit, *overloads)


    def saveCredit(self, monday, credit):
        filename = self._creditFile(monday)
        credit.dump(str(filename))





#vim: ts=4 sw=4 et
