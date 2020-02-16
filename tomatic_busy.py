#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function
from tomatic import busy
import sys
import click
from yamlns import namespace as ns
from tomatic import __version__

def open(*args, **kwd):
	import codecs
	return codecs.open(encoding='utf8', *args, **kwd)

def table(data):
	return '\n'.join('\t'.join(unicode(c) for c in row) for row in data)

def nextMonday(date):
	import datetime
	today = date or datetime.datetime.today()
	return str(today + datetime.timedelta(days=(7-today.weekday()) or 7))

def busyTable(monday, *filenames, **kwds):
	from itertools import product as xproduct
	availability = dict(
		((dia,hora), set())
	for dia, hora in xproduct(busy.weekdays, range(busy.nturns))
		)

	for filename in filenames:
		def errorHandler(msg):
			raise Exception(
				"{}:{}".format(filename, msg))

		with open(filename) as thefile:	
			allentries = busy.parseBusy(thefile, errorHandler)
			thisweekentries = busy.onWeek(monday, allentries)
			for entry in thisweekentries:
				for hora, isBusy in enumerate(entry.turns):
					if isBusy!='1': continue
					busyWeekDays = [entry.weekday] if entry.weekday else busy.weekdays
					for dia in busyWeekDays:
						if 'optional' in kwds and kwds['optional'] and not entry.optional:
							continue
						if 'required' in kwds and kwds['required'] and entry.optional:
							continue
						availability[dia, hora].add(entry.person)
	return availability



@click.command()
@click.help_option()
@click.version_option(__version__)
@click.argument('date',
	default=None,
	)
@click.argument('person',
	required=False,
	default=None,
	)
@click.option('--optional',
	help=u"Mira només quants son opcionals",
	is_flag=True,
	)
@click.option('--required',
	help=u"Mira només quants son obligats",
	is_flag=True,
	)
def cli(date, person, optional, required):
	u'Manages busy hours that persons cannot be attending phone'
	print(optional)
	date = busy.isodate(date)
	busydays = busyTable(date,
		'oneshot.conf',
		'indisponibilitats.conf',
		optional=optional,
		required=required,
		)
	print(table(
		[['']+busy.weekdays] +
		[
			[hour]+
			[
				len(busydays[weekday, hour])
				for weekday in busy.weekdays
			]
			for hour in xrange(busy.nturns)
		]))

	print(table(
		[['']+busy.weekdays] +
		[
			[hour]+
			[
				','.join(busydays[weekday, hour])
				for weekday in busy.weekdays
			]
			for hour in xrange(busy.nturns)
		]))
	if person:
		print(table(
			[['']+busy.weekdays] +
			[
				[hour]+
				[
					1 if person in busydays[weekday, hour] else 0
					for weekday in busy.weekdays
				]
				for hour in xrange(busy.nturns)
			]))


if __name__=='__main__':
	cli()


