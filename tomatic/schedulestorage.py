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

    def _checkMonday(self, monday):
        date = datetime.datetime.strptime(monday,'%Y-%m-%d')
        if not date.weekday(): return
        weekdays = "monday tuesday wednesday thursday friday saturday sunday".split()
        raise Exception("{} is not a monday but a {}".format(
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

    def load(self, week):
        self._checkMonday(week)
        filename = self._timetableFile(week)
        try:
            return ns.load(str(filename))
        except IOError:
            raise KeyError(week)

    def save(self, value):
        self._checkMonday(value.week)
        filename = self._timetableFile(value.week)
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

#vim: ts=4 sw=4 et
