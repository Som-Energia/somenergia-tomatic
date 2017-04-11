#!/usr/bin/env python
# -*- utf8 -*-

from bisect import bisect

def weekday(date):
    if not hasattr(weekday, '_weekdays'):
        weekday._weekdays = "dl dm dx dj dv ds dg".split()
    return weekday._weekdays[date.weekday()]


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




# vim: ts=4 sw=4 et
