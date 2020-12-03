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





"""
Remainders for full queue info to recover whenever we are back to direct asterisk usage
"""

def extractQueueInfo(output):
    return [
        extractQueuepeerInfo(line)
        for line in output.splitlines()
        if line.strip().startswith('SIP/')
    ]

def lala():
    if fake:
        output = u"""\
somenergia has 0 calls (max unlimited) in 'leastrecent' strategy (4s holdtime, 340s talktime), W:0, C:159, A:88, SL:100.0% within 30s
   Members: 
      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) (paused) has taken 6 calls (last was 181 secs ago)
      SIP/3188@bustia_veu (SIP/3188) (ringinuse disabled) (realtime) (in call) (In use) has taken 3 calls (last was 630 secs ago)
      SIP/3043@bustia_veu (SIP/3043) (ringinuse disabled) (realtime) (Not in use) has taken 4 calls (last was 257 secs ago)
      SIP/3084@bustia_veu (SIP/3084) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 187 secs ago)
      SIP/2905@bustia_veu (SIP/2905) (ringinuse disabled) (realtime) (Ringing) (In use) has taken 5 calls (last was 564 secs ago)
      SIP/3048@bustia_veu (SIP/3048) (ringinuse disabled) (realtime) (Not in use) has taken 4 calls (last was 189 secs ago)
      SIP/2902@bustia_veu (SIP/2902) (ringinuse disabled) (realtime) (in call) (In use) has taken 2 calls (last was 1367 secs ago)
   No Callers
"""
    else:
        remote = Remote(**dbconfig.tomatic.ssh)
        output = remote.run("asterisk -rx 'queue show {}'".format(queue))

    info = extractQueueInfo(output)
    if raw:
        click.echo(output)
    if sql:
        sortida = remote.run('''echo 'select callerid, paused, sippeers.* from queue_members join sippeers on queue_members.interface = concat("SIP/", sippeers.name);' | sudo mysql asterisk''')
        click.echo(sortida)




# vim: ts=4 sw=4 et
