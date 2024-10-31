# -*- coding: utf-8 -*-

from yamlns import namespace as ns
from .. import persons
from ..remote import Remote
from ..config import secrets

"""
This is a patch until we find a way to obtain this info
from the realtime db.
"""

def extract(pattern, string, default=None):
    import re
    matches = re.search(pattern, string)
    return matches.group(1) if matches else default

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


# TODO: Untested
def queueFromSsh(queue):
    remote = Remote(**secrets('tomatic.ssh'))
    output = remote.run("asterisk -rx 'queue show {}'".format(self._queue))
    return [
        extractQueuepeerInfo(line)
        for line in output.splitlines()
        if line.strip().startswith('SIP/')
    ]



"""
Remainings for full queue info to recover whenever we are back to direct asterisk usage
"""

def ignored():
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
    if sql:
        remote = Remote(**secrets('tomatic.ssh'))
        sortida = remote.run('''echo 'select callerid, paused, sippeers.* from queue_members join sippeers on queue_members.interface = concat("SIP/", sippeers.name);' | sudo mysql asterisk''')
        click.echo(sortida)



# vim: ts=4 sw=4 et
