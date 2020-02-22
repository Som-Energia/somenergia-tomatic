#!/usr/bin/env python
# -*- coding: utf-8 -*-

from past.builtins import basestring
import datetime
from yamlns import namespace as ns
from consolemsg import out, u
from pathlib2 import Path

def open(*args, **kwd):
	import codecs
	return codecs.open(encoding='utf8', *args, **kwd)

nturns = 4
weekdays = 'dl dm dx dj dv'.split()

def isodate(datestr):
	return datetime.datetime.strptime(datestr, "%Y-%m-%d").date()


def onWeek(monday, singularBusies):
	"""
	Generator that takes a serie of fixed date busies,
	filters outs the ones outside the week starting
	on monday, and turns the date into a weekday.
	"""
	friday = monday+datetime.timedelta(days=4)
	for b in singularBusies:
		if 'weekday' in b:
			yield b
			continue
		if b.date < monday: continue
		if b.date > friday: continue
		weekday = weekdays[b.date.weekday()]
		result = ns(b, weekday = weekday)
		del result.date
		yield result

def formatItem(item):
	# TODO: Manage no days, multiple days and no hours
	return u"{forcedmark}{person} {dateorweekday} {turns} # {reason}\n".format(
		dateorweekday = item.get('date') or item.get('weekday'),
		forcedmark = '' if item.optional else '+',
		**item)

def parseBusy(lines, errorHandler=None):
	"Parses weekly events from lines"
	def error(msg):
		raise Exception(msg)
	if errorHandler: error = errorHandler
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

def justPerson(person, entries):
	def wrap(entry):
		entry = ns(entry)
		# TODO: how necessary is that?
		if 'date' in entry: entry.date=format(entry.date)
		del entry.person
		return entry
	return [
		wrap(entry)
		for entry in entries
		if entry.person == person
	]

def updatePerson(filename, person, newPersonEntries, handler=None):

	with open(filename) as ifile:
		oldEntries = [e for e in parseBusy(ifile.readlines(), handler)]

	return ''.join([
		formatItem(entry)
		for entry in oldEntries
		if entry.person != person
		] + [
		formatItem(ns(entry, person=person))
		for entry in newPersonEntries
		])

def busy(person):
	"""API Entry point to obtain person's busy"""
	errors = []
	def indisponibilitats(filename):
		def handler(m):
			errors.append(filename+':'+m)
		with open(filename) as f:
			return justPerson(person, parseBusy(f, handler))
	return ns(
		weekly = indisponibilitats('indisponibilitats.conf'),
		oneshot = indisponibilitats('oneshot.conf'),
		errors=errors,
		)

def checkEntry(kind, entry):
	fields = set((
		'reason',
		'optional',
		'turns',
		'weekday' if kind == 'weekly' else 'date',
	))
	for a in entry.keys():
		if a not in fields:
			raise Exception("Unexpected field '{}'".format(a))
	for a in fields:
		if a not in entry.keys():
			raise Exception("Missing field '{}'".format(a))
	if 'weekday' in entry:
		if entry.weekday and entry.weekday not in "dl dm dx dj dv ds dg".split():
			raise Exception(
				"Bad weekday '{}', should be dl, dm, dx, dj, dv or empty"
				.format(entry.weekday))
	if 'date' in entry:
		try:
			entry.date = isodate(entry.date)
		except ValueError:
			raise Exception(
				"Field 'date' should be a date but was '{}'"
				.format(entry.date))
	if type(entry.optional) != bool:
		raise Exception(
			"Bad value for 'optional'. Expected a boolean but was '{}'"
			.format(entry.optional))

	if not isinstance(entry.reason, basestring):
		raise Exception(
			"Invalid type '{}' for field 'reason'"
			.format(type(entry.reason).__name__))

	if len(entry.turns) != nturns or not all(x in '01' for x in entry.turns):
		raise Exception(
			"Attribute 'turns' should be a text with {} ones or zeroes, "
			"but was '{}'"
			.format(nturns, entry.turns))

	if not entry.reason.strip():
		raise Exception("No heu indicat el motiu de la indisponibilitat")

def update_busy(person, data):
	"""API Entry point to update person's busy"""
	files = [
		('indisponibilitats.conf', 'weekly'),
		('oneshot.conf', 'oneshot'),
	]
	output=dict()
	try:
		for filename, attribute in files:
			for entry in data[attribute]:
				checkEntry(attribute, entry)
			def handler(error):
				raise Exception("{}: {}".format(filename, error))
			output[attribute] = updatePerson(filename, person, data[attribute], handler)
		for filename, attribute in files:
			with open(filename,'w') as f:
				f.write(output[attribute])
	except Exception as e:
		out("{} {}", e, entry)
		return ns(
			result='error',
			message=format(e),
			)
	return ns(result='ok')

def laborableWeekDays(monday, holidays=None):

	monday = monday + datetime.timedelta(days=-monday.weekday())
	if not holidays:
		# TODO: This should be taken from No Toi Web App
		holidaysFile = Path('holidays.conf')
		content = holidaysFile.read_text(encoding='utf8')
		holidays = [
			line.split('\t')
			for line in content.split('\n')
			if line.strip()
		]
	holidays = set(
		isodate(date)
		for date, description  in holidays
	)
	return [
		w
		for i,w in enumerate(weekdays)
		if monday + datetime.timedelta(days=i) not in holidays
		]

class BusyTable(object):
	"""Fast lookup table of whether someone is busy at some turn"""
	def __init__(self, days, nhours, persons):
		self._days = days
		self._table = {
			(day, hour, person): False
			for person in persons
			for hour in range(nhours)
			for day in days
		}

	def isBusy(self, day, hour, person):
		return self._table.get((day,hour,person), True)

	def setBusy(self, day, hour, person, isBusy=True):
		if (day,hour,person) not in self._table:
			raise Exception(
				"{} not in the list, cannot be unbusied"
				.format(person))

		self._table[(day,hour,person)] = isBusy



	def load(self, filename, monday, errorHandler=None, justOptional=False, justRequired=False):
		with open(filename) as thefile:
			allentries = parseBusy(thefile, errorHandler)
			thisweekentries = onWeek(monday, allentries)
			for entry in thisweekentries:
				if justOptional and not entry.optional: continue
				if justRequired and entry.optional: continue
				for hora, isBusy in enumerate(entry.turns):
					if isBusy!='1': continue
					weekdays = [entry.weekday] if entry.weekday else self.dies
					for dia in weekdays:
						self.setBusy(dia, hora, entry.person)

	def dayBusy(self, day, person):
		return ''.join(
			'1' if self.isBusy(day, hour, person) else '0'
			for hour in range(4))




# vim: noet ts=4 sw=4
