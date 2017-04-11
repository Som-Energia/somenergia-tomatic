#!/usr/bin/env python
# -*- utf8 -*-

from bisect import bisect


def peekQueue(schedule, day, hour):
    if schedule is None: return []
    turn = bisect(schedule.hours, hour)
    if turn <=0: return [] # Turn before first hour
    try:
        return schedule.timetable[day][turn-1]
    except IndexError: # Turn after first hour
        return []
    except KeyError: # Day not found
        return []






class Chooser(object):
    def __init__(self):
        self._config = None

    def reconfigure(self, config):
        self._config = config

    def currentQueue(self, today, now):
        if self._config is None: return []
        turn = bisect(self._config.hours, now)
        if turn <=0: return []
        try:
            return self._config.timetable[today][turn-1]
        except IndexError:
            return []
        except KeyError:
            return []


# vim: ts=4 sw=4 et
