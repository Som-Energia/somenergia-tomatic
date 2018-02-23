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
	Weekly busies are considered errors.
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
	optional = need != u'Necessària'
	return ns(
		optional = optional,
		person = transliterate(who),
		turns = bitmap,
		reason = comment,
		date = theDay,
		)

def gform2Singular(lines):
	return ( gformDataLine(l) for l in lines[1:] )

def onWeek(monday, singularBusies):
	"""
	Generator that takes a serie of fixed date busies,
	filters outs the ones outside the week starting
	on monday, and turns the date into a weekday.
	"""
	sunday = monday+datetime.timedelta(days=6)
	for b in singularBusies:
		if b.date < monday: continue
		if b.date > sunday: continue
		weekday = u'dl dm dx dj dv ds dg'.split()[b.date.weekday()]
		result = ns(b, weekday = weekday)
		del result.date
		yield result

def formatItem(item):
	# TODO: Manage no days, multiple days and no hours
	return u"{forcedmark}{person} {dateorweekday} {turns} # {reason}\n".format(
		dateorweekday = item.get('date') or item.get('weekday'),
		forcedmark = '' if item.optional else '+',
		**item)

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
		row, comment = l.split('#',1) if '#' in l else (l,'')
		items = row.split()
		if not items: continue
		if not comment.strip():
			error(
				"{}: Your have to specify a reason "
				"for the busy event after a # sign"
				.format(i))
			# non fatal if a handler is provided

		name = items.pop(0)
		forced = name[0:1] == '+'
		if forced: name = name[1:]

		date = None
		weekday = '' # all weekdays
		if items and items[0] in weekdays:
			weekday = items.pop(0)
		elif items:
			try: date = isodate(items[0])
			except ValueError: pass
			else: items.pop(0)

		turns = items[0].strip() if items else '1'*nturns
		if len(turns)!=nturns or any(t not in '01' for t in turns):
			error(
				"{}: Expected busy string of lenght {} "
				"containing '1' on busy hours, found '{}'"
				.format(i, nturns, turns))
			continue
		when = ns(date=date) if date else ns(weekday=weekday)
		yield ns(
			person=name,
			turns=turns,
			reason=comment.strip(),
			optional=not forced,
			**when
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

def busy(person):
	config = ns.load('config.yaml')
	errors = []
	def indisponibilitats(filename, tipus):
		def handler(m):
			errors.append(filename+':'+m)
		with open(filename) as f:
			return personBusyness(person, tipus(f, handler), dict(
				optional=False,
				))
	return ns(
		weekly = indisponibilitats('indisponibilitats.conf', parseBusy),
		oneshot = indisponibilitats('indisponibilitats-oneshot.conf', parseBusy),
		errors=errors,
		)

def update_busy(person, data):
	# TODO: Implement this
	print data.dump()
	return ns(status='ok')


# vim: noet ts=4 sw=4
