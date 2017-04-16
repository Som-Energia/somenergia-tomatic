#!/usr/bin/env python
# -*- coding: utf8 -*-

from bisect import bisect
from datetime import timedelta
from yamlns import namespace as ns

def weekday(date):
    "Given a date gives the catalan short for the weekday"
    if not hasattr(weekday, '_weekdays'):
        weekday._weekdays = "dl dm dx dj dv ds dg".split()

    return weekday._weekdays[date.weekday()]

def weekstart(date):
    "Given a date retunrs the monday of the week"
    return date - timedelta(days=date.weekday())

def nextweek(date):
    return date + timedelta(days=7-date.weekday())

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

class Scheduling(object):

    def __init__(self, yaml):
        self._data = ns.loads(yaml)

    def extension(self,name):
        extensions = self._data.extensions
        if name not in extensions:
            return None
        return str(extensions[name])

    def extensionToName(self, extension):
        extensions = self._data.extensions
        inverse = dict(item[::-1]
            for item in extensions.items())
        return inverse[int(extension)]

    def properName(self, name):
        names = self._data.get('names',{})
        if name in names:
            return names[name]
        return name.title()

    def intervals(self):
        hours = self._data.hours
        return ['-'.join((h1,h2)) for h1,h2 in zip(hours,hours[1:]) ]


# vim: ts=4 sw=4 et
