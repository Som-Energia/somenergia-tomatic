#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import unicode_literals
from bisect import bisect
from datetime import timedelta
from yamlns import namespace as ns

def weekday(date):
    "Returns the catalan short for the weekday of the given date"
    if not hasattr(weekday, '_weekdays'):
        weekday._weekdays = "dl dm dx dj dv ds dg".split()

    return weekday._weekdays[date.weekday()]

def weekstart(date):
    "Returns the monday of the week of the given date"
    return date - timedelta(days=date.weekday())

def nextweek(date):
    "Returns the start of the next week of the given date"

    return date + timedelta(days=7-date.weekday())

def choosers(now):
    """Given a datetime, returns a tuple: week, dow and time
    suitable of be used to choose the schedule and the
    slot within with the lines"""
    return (
        str(weekstart(now).date()),
        weekday(now),
        "{:%H:%M}".format(now)
        )

class Scheduling(object):

    def __init__(self, yaml):
        if type(yaml) in (ns, dict):
            self._data = ns(yaml) # untested
        else:
            self._data = ns.loads(yaml)

    def extension(self,name):
        extensions = self._data.extensions
        if name not in extensions:
            return None
        return str(extensions[name])

    def extensionToName(self, extension):
        extensions = self._data.extensions
        inverse = dict([str(x) for x in item[::-1]]
            for item in extensions.items())
        try:
            return inverse[str(extension)]
        except KeyError:
            return extension

    def properName(self, name):
        names = self._data.get('names',{})
        if name in names:
            return names[name]
        return name.title()

    def intervals(self):
        hours = self._data.hours
        return ['-'.join((h1,h2)) for h1,h2 in zip(hours,hours[1:]) ]

    def peekInterval(self, time):
        if not 'hours' in self._data:
            raise Exception("Schedule with no hours attribute")
        turn = bisect(self._data.hours, time)
        if turn<=0: return None
        if turn>=len(self._data.hours):
            return None
        return turn-1

    def peekQueue(self, day, hour):
        schedule = self._data
        turn = self.peekInterval(hour)

        if day not in schedule.timetable:
            return [] # Holidays

        if turn is None:
            return [] # Not in phone hours

        if type(schedule.timetable[day]) is list:
            return schedule.timetable[day][turn]

        return schedule.timetable[day][turn+1]

    def data(self):
        return ns(self._data)

    @classmethod
    def fromSolution(cls, config, solution, date=None):
        return Scheduling(
            solution2schedule(
                config=config,
                solution=solution,
                date=date,
            ))

def solution2schedule(config, solution, date=None):
    nhours = len(config.hours)-1
    tt = ns(
        (day, [
            [None for i in range(config.nTelefons)]
            for j in range(nhours)
        ])
        for day in config.diesVisualitzacio
    )
    for day in config.diesVisualitzacio:
        for time in range(nhours):
            for tel in range(config.nTelefons):
                tt[day][time][tel]=solution.get(
                    (day,time,tel),
                    'festiu'
                ).lower()
    import datetime
    if not date:
        date = nextweek(datetime.date.today())
    else:
        date = weekstart(date)
    result=ns()
    result.week =str(date)
    result.days = config.diesVisualitzacio
    result.hours = config.hours
    result.turns = ["T"+str(i+1) for i in range(config.nTelefons)]
    result.timetable = tt
    result.colors = config.colors
    result.extensions = config.extensions
    result.names = config.names
    return result




# vim: ts=4 sw=4 et
