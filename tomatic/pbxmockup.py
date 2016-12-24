# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from yamlns import namespace as ns

def weekday(date):
    weekdays = "dl dm dx dj dv ds dg".split()
    return weekdays[date.weekday()]

class PbxMockup(object):
    """
    A PbxMockup emulates the operations tomatic needs from
    a Pbx without having real effect on any PBX.
    """

    def __init__(self):
        self._configuration = ns.loads(u"""
            timetable: {}
            hores: []
            """)
        self._paused = set()

    def reconfigure(self, configuration):
        # TODO: Test later modifications on configuration do not affect inner
        self._configuration = ns.loads(configuration.dump())

    def currentQueue(self):
        timetable = self._configuration.timetable
        now = datetime.now()
        from bisect import bisect
        currentHour = "{0:%H:%m}".format(now)
        turn = bisect(self._configuration.hores, currentHour)
        wd = weekday(now)
        if wd not in timetable: return []

        if type(timetable[wd]) is list:
            turn-=1
            if turn<0: return []

        try:
            lines = timetable[wd][turn]
        except IndexError: return []
        except KeyError: return []

        return [
            ns( key=who, paused= who in self._paused)
            for who in timetable[wd][turn]
            ]

    def pause(self, who):
        "Temporary removes the operator from the queue"
        self._paused.add(who)

    def restore(self, who):
        "Puts back the operator to the queue"
        if who in self._paused:
            self._paused.remove(who)



# vim: ts=4 sw=4 et
