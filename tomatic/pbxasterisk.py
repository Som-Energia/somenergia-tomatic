# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from yamlns import namespace as ns
from paramiko import SSHClient,AutoAddPolicy, SFTPClient

def weekday(date):
    weekdays = "dl dm dx dj dv ds dg".split()
    return weekdays[date.weekday()]

class Remote(object):
    def __init__(self, username, host):
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(host, username=username)

    def __enter__(self):
        return self

    def __exit__(self, *excl):
        return self.ssh.__exit__(*excl)

    def read(self, filename):
        sftp = self.ssh.open_sftp()
        with sftp.open(filename, 'r') as f:
            return f.read()
        


def remoteread(user, host, filename):
    with Remote(user, host) as remote:
        return remote.read(filename)


def remotewrite(user, host, filename, content):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=user)
        sftp = ssh.open_sftp()
        with sftp.open(filename, 'w') as f:
            f.write(content)

def remoterun(user, host, command):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=user)
        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.close()
        return stdout.read()

class Pbx(object):
    """
    Pbx interface implementation based on Asterisk.
    """

    def __init__(self,now=None):
        self._configuration = ns.loads(u"""
            timetable: {}
            hours: []
            """)
        if now: self._now = now
        self._paused = set()
        self._extraLines = list()

    def _now(self):
        return datetime.now()

    def reconfigure(self, configuration):
        return

    def scheduledQueue(self):
        return
        return [
            ns( key=who, paused= who in self._paused)
            for who in timetable[wd][turn]
            ]

    def currentQueue(self):
        return []
        return self.scheduledQueue() + [
            ns( key=who, paused= who in self._paused)
            for who in self._extraLines
            ]

    def pause(self, who):
        "Temporary removes the operator from the queue"

    def resume(self, who):
        "Puts back the operator to the queue"

    def addLine(self, person):
        "Adds a new line at the end of the queue"


# vim: ts=4 sw=4 et
