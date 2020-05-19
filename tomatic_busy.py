#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from tomatic import busy
import sys
import click
from yamlns import namespace as ns
from consolemsg import u, out
from tomatic import __version__
try:
	from pathlib2 import Path
except ImportError:
	from pathlib import Path

def open(*args, **kwd):
	import codecs
	return codecs.open(encoding='utf8', *args, **kwd)

def table(data):
	return '\n'.join('\t'.join(u(c) for c in row) for row in data)

def nextMonday(date):
	import datetime
	today = date or datetime.datetime.today()
	return format(today + datetime.timedelta(days=(7-today.weekday()) or 7))

@click.command()
@click.help_option()
@click.version_option(__version__)
@click.argument('date',
	default=None,
	)
@click.argument('sandbox',
	default='',
	)
@click.option('--optional',
	help=u"Mira només quants son opcionals",
	is_flag=True,
	)
@click.option('--required',
	help=u"Mira només quants son obligats",
	is_flag=True,
	)
def cli(date, sandbox, optional, required):
	u'Manages busy hours that persons cannot be attending phone'
	date = busy.isodate(date)
	sandbox=Path(sandbox)
	activePersons = ns.load(sandbox/'ponderatedideal-{}.yaml'.format(date)).keys()
	busytable = busy.BusyTable(
		days=busy.weekdays,
		nhours = busy.nturns,
		persons = activePersons,
		)
	for busyfile in [
		'oneshot.conf',
		'indisponibilitats.conf',
		'indisponibilitats-vacances.conf',
		]:
		busytable.load(format(sandbox/busyfile), date, justOptional=optional, justRequired=required)

	reasonTable = busytable.explain()
	out("\n# Resum\n")
	out(table(
		[['']+busy.weekdays] +
		[
			[hour]+
			[
				len(reasonTable[weekday, hour])
				for weekday in busy.weekdays
			]
			for hour in range(busy.nturns)
		]))

	out("\n# Detall\n")
	for weekday in busy.weekdays:
		out("\n## {}\n", weekday)
		for hour in range(busy.nturns):
			busyAtTime = reasonTable.get((weekday, hour), {})
			out("\n### {}a hora ({})\n", hour+1, len(busyAtTime))
			for person, reasons in sorted(busyAtTime.items()):
				for reason in reasons:
					out("- {}: {}", person, reason)


if __name__=='__main__':
	cli()


