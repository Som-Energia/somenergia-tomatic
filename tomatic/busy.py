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
def isodate(datestr):
	return datetime.datetime.strptime(datestr, "%Y-%m-%d").date()


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

from yamlns import namespace as ns

def parseBusy(lines, errorHandler=None):
	"Parses weekly events from lines"
	def error(msg):
		raise Exception(msg)
	if errorHandler: error = errorHandler
	nturns = 4
	weekdays = 'dl dm dx dj dv'.split()
	for i, l in enumerate(lines,1):
		if not l.strip(): continue
		if '#' not in l:
			error(
				"{}: Your have to specify a reason "
				"for the busy event after a # sign"
				.format(i))
			continue
		row, comment = l.split('#',1)
		if not row: continue
		if not comment.strip():
			error(
				"{}: Your have to specify a reason "
				"for the busy event after a # sign"
				.format(i))
			continue
		items = row.split()
		if items[1:] and items[1] in weekdays:
			weekday = items[1]
			turns = items[2:]
		else:
			weekday = ''
			turns = items[1:]
		turns = turns[0].strip() if turns else '1'*nturns
		if len(turns)!=nturns or any(t not in '01' for t in turns):
			error(
				"{}: Expected busy string of lenght {} "
				"containing '1' on busy hours, found '{}'"
				.format(i, nturns, turns))
			continue
		yield ns(
			person=items[0],
			weekday=weekday,
			turns=turns,
			reason=comment.strip(),
			)

def parseOneshotBusy(lines, errorHandler=None):
	"Parses weekly events from lines"
	def error(msg):
		raise Exception(msg)
	if errorHandler: error = errorHandler
	nturns = 4
	weekdays = 'dl dm dx dj dv'.split()
	for i, l in enumerate(lines,1):
		if not l.strip(): continue
		if '#' not in l:
			error(
				"{}: Your have to specify a reason "
				"for the busy event after a # sign"
				.format(i))
			continue
		row, comment = l.split('#',1)
		if not row: continue
		if not comment.strip():
			error(
				"{}: Your have to specify a reason "
				"for the busy event after a # sign"
				.format(i))
			continue
		items = row.split()
		date = isodate(items[1])
		turns = items[2:]
		turns = turns[0].strip() if turns else '1'*nturns
		if len(turns)!=nturns or any(t not in '01' for t in turns):
			error(
				"{}: Expected busy string of lenght {} "
				"containing '1' on busy hours, found '{}'"
				.format(i, nturns, turns))
			continue
		yield ns(
			person=items[0],
			date=date,
			turns=turns,
			reason=comment.strip(),
			)


def personBusyness(person, entries, extra):
	result=[]
	for entry in entries:
		if entry.person != person:
			continue
		del entry.person
		entry.update(extra)
		if 'date' in entry:
			entry.date=str(entry.date)
		result.append(entry)
	return result

def personSingulars(person, lines, extra):
	result=[]
	for aperson, date, turns, reason in lines:
		if aperson != person:
			continue
		entry = ns(
			date=date,
			turns=turns,
			reason=reason,
			**extra
			)
		result.append(entry)
	return result

def busy(person):
	import busy
	from sheetfetcher import SheetFetcher
	config = ns.load('config.yaml')
	errors = []
	def indisponibilitats(filename, tipus):
		def handler(m):
			errors.append(filename+':'+m)
		with open(filename) as f:
			return busy.personBusyness(person, tipus(f, handler), dict(
				optional=False,
				))

	return ns(
		weekly = indisponibilitats('indisponibilitats.conf'), parseBusy),
		oneshot = indisponibilitats('indisponibilitats-oneshot.conf', parseOneshotBusy),
		errors=errors,
		)


# vim: noet ts=4 sw=4
