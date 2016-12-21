# -*- encoding: utf-8 -*-

from yamlns import namespace as ns
import os
import datetime
import glob

class Storage(object):
    "Stores schedules by week"

    def __init__(self, dirname):
        self._dirname = dirname

    def _filename(self, week):
        week = datetime.datetime.strptime(week,'%Y-%m-%d')
        return os.path.join(
            self._dirname,
            "graella-{:%Y-%m-%d}.yaml"
            .format(week))

    def load(self, week):
        filename = self._filename(week)
        try:
            return ns.load(filename)
        except IOError:
            raise KeyError(week)

    def save(self, value):
        filename = self._filename(value.date)
        value.dump(filename)

    def list(self):
        pattern = os.path.join(
            self._dirname,
            'graella-*.yaml'
            )
        return [
            filename[-len('yyyy-mm-dd.yaml'):-len('.yaml')]
            for filename in glob.glob(pattern)
            ]

#vim: ts=4 sw=4 et
