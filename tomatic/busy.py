#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

class GFormError(Exception): pass

# TODO: Move it to a utility module and test it
def transliterate(word):
	word=unicode(word).lower()
	for old, new in zip(
		u'àèìòùáéíóúçñ',
		u'aeiouaeioucn',
	) :
		word = word.replace(old,new)
	return word

def gformDataLine(line):
	"""
	Turns an entry from the gform into a proper singular busy date.
	"""
	_, who, day, weekday, hours, need, comment = line
	if weekday and day:
		raise GFormError(
			"Indisponibilitat especifica dia puntual {} "
			"i dia de la setmana {}"
			.format(day,weekday))
	if weekday:
		raise GFormError(
			"Hi ha indisponibilitats permaments al drive, "
			"afegeix-les a ma i esborra-les del drive")
	theDay = datetime.datetime.strptime(day, "%d/%m/%Y").date()
	startHours = [ h.split(':')[0].strip() for h in hours.split(',')]
	bitmap = ''.join((
		('1' if '9' in startHours else '0'),
		('1' if '10' in startHours else '0'),
		('1' if '11' in startHours else '0'),
		('1' if '12' in startHours else '0'),
	))
	return transliterate(who), theDay, bitmap, comment

def gform2Singular(lines):
	return ( gformDataLine(l) for l in lines[1:] )

def singular2Weekly(monday, singularBusies):
	sunday = monday+datetime.timedelta(days=6)
	for who, day, bitmap, comment in singularBusies:
		if day < monday: continue
		if day > sunday: continue
		weekdayShort = u'dl dm dx dj dv ds dg'.split()[day.weekday()]
		yield who, weekdayShort, bitmap, comment

def formatWeekly(weekly):
	# TODO: Manage no days, multiple days and no hours
	return u"{} {} {} # {}\n".format(*weekly)

def parseBusy(lines):
	"Parses weekly events from lines"
	if False: yield



# vim: noet ts=4 sw=4
