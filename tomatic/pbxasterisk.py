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
        self.backend = DbAsterisk(*dbargs, **dbkwd)

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
            self.backend.setQueue('somenergia', [])
            return
        week, dow, time = choosers(when)
        self.backend.setQueue('somenergia', [
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
            in self.backend.queue('somenergia')
        ]

    
    def pause(self, name):
        sched = self._currentSched()
        self.backend.pause('somenergia', sched.extension(name))
    def resume(self, name):
        sched = self._currentSched()
        self.backend.resume('somenergia', sched.extension(name))

    def addLine(self, name):
        sched = self._currentSched()
        self.backend.add('somenergia', sched.extension(name))


def extract(pattern, string, default=None):
    import re
    matches = re.search(pattern, string)
    return matches.group(1) if matches else default

from . import persons

def extractQueuepeerInfo(line):
    peer = ns()
    peer.extension = extract('\(SIP/([0-9]+)\)', line, '????')
    peer.key = persons.byExtension(peer.extension)
    peer.name = persons.name(peer.key)
    peer.paused = '(paused)' in line
    peer.ringing = '(Ringing)' in line
    peer.disconnected = '(Unavailable)' in line
    peer.available = '(Not in use)' in line
    peer.incall = '(in call)' in line
    peer.ncalls = int(extract('has taken ([0-9]+) calls', line, '0'))
    peer.secondsSinceLastCall = int(extract('last was ([0-9]+) secs ago', line, '0'))
    import re
    peer.flags = [ flag
        for flag in re.findall(r"\(([^)]+)\)",line)
        if flag not in [
            'Not in use',
            'In use', # ignored, expected to be negated of 'Not in use'
            'Ringing',
            'in call',
            'Unavailable',
            'paused',
            'realtime', # ignored
            'ringinuse disabled', # ignored
        ]
        and not flag.startswith('has taken ')
        and not flag.startswith('last was ')
        and not flag.startswith('SIP/')
    ]
    return peer


# vim: ts=4 sw=4 et
