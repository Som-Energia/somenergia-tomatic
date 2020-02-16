# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datetime import datetime
from yamlns import namespace as ns
from .scheduling import weekday, Scheduling

class PbxMockup(object):
    """
    A PbxMockup emulates the operations tomatic needs from
    a Pbx without having real effect on any PBX.
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
        # TODO: Test later modifications on configuration do not affect inner
        self._configuration = ns.loads(configuration.dump())

    def scheduledQueue(self):
        timetable = self._configuration.timetable
        now = self._now()
        currentHour = "{0:%H:%m}".format(now)
        wd = weekday(now)

        schedule = Scheduling(self._configuration)

        return [
            ns( key=who, paused= who in self._paused)
            for who in schedule.peekQueue(wd, currentHour)
            ]

    def currentQueue(self):
        return self.scheduledQueue() + [
            ns( key=who, paused= who in self._paused)
            for who in self._extraLines
            ]

    def pause(self, who):
        "Temporary removes the operator from the queue"
        self._paused.add(who)

    def resume(self, who):
        "Puts back the operator to the queue"
        if who in self._paused:
            self._paused.remove(who)

    def addLine(self, person):
        "Adds a new line at the end of the queue"
        self._extraLines.append(person)


# vim: ts=4 sw=4 et
