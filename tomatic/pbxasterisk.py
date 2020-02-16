# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .schedulestorage import Storage
from .dbasterisk import DbAsterisk
from .scheduling import choosers, Scheduling
import datetime
from yamlns import namespace as ns

class PbxAsterisk(object):

    def __init__(self, path, *dbargs, **dbkwd):
        self.storage = Storage(path)
        self.db = DbAsterisk(*dbargs, **dbkwd)

    def _currentSched(self, when=None):
        when = when or datetime.datetime.now()
        week, dow, time = choosers(when)
        try:
            yaml=self.storage.load(week)
        except KeyError:
            return None
        return Scheduling(yaml)

    def setSchedQueue(self, when):
        sched = self._currentSched(when)
        if sched is None:
            self.db.setQueue('somenergia', [])
            return
        week, dow, time = choosers(when)
        self.db.setQueue('somenergia', [
            sched.extension(name)
            for name in sched.peekQueue(dow, time)
        ])

    def currentQueue(self):
        sched = self._currentSched()
        if sched is None:
            return []
        return [
            ns(
                key=sched.extensionToName(extension),
                paused=bool(paused),
            )
            for extension, paused
            in self.db.queue('somenergia')
        ]

    
    def pause(self, name):
        sched = self._currentSched()
        self.db.pause('somenergia', sched.extension(name))
    def resume(self, name):
        sched = self._currentSched()
        self.db.resume('somenergia', sched.extension(name))

    def addLine(self, name):
        sched = self._currentSched()
        self.db.add('somenergia', sched.extension(name))



# vim: ts=4 sw=4 et
