# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from yamlns import namespace as ns
from paramiko import SSHClient,AutoAddPolicy, SFTPClient
from .htmlgen import HtmlGenFromYaml

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

    def write(self, filename, content):
        sftp = self.ssh.open_sftp()
        with sftp.open(filename, 'w') as f:
            f.write(content)

    def run(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.close()
        return stdout.read()

def remoteread(user, host, filename):
    with Remote(user, host) as remote:
        return remote.read(filename)


def remotewrite(user, host, filename, content):
    with Remote(user, host) as remote:
        remote.write(filename, content)

def remoterun(user, host, command):
    with Remote(user, host) as remote:
        return remote.run(command)

from Asterisk.Manager import Manager

class Pbx(object):
    """
    Pbx interface implementation based on Asterisk.
    """

    def __init__(self, user, host, path, **config):
        self._manager = Manager(**config)
        self._user = user
        self._host = host
        self._path = path

    def reconfigure(self, configuration):
        h = HtmlGenFromYaml(configuration)
        asterisk_conf = h.asteriskParse()
        with Remote(self._user, self._host) as remote:
            remote.write(self._path, asterisk_conf)
        self._manager.Command('reload')

    def scheduledQueue(self):
        return
        return [
            ns( key=who, paused= who in self._paused)
            for who in timetable[wd][turn]
            ]

    def currentQueue(self):
        return self._manager.Queues() or []

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
