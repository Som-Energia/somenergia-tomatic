# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from yamlns import namespace as ns
from paramiko import SSHClient,AutoAddPolicy, SFTPClient
from .htmlgen import HtmlGenFromYaml

def weekday(date):
    weekdays = "dl dm dx dj dv ds dg".split()
    return weekdays[date.weekday()]

from .remote import Remote, remoteread, remotewrite, remoterun

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
