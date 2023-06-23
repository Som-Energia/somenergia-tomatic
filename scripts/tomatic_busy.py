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
	from pathlib import Path
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

def getActivePersons(config, sandbox):
	from tomatic.retriever import downloadIdealLoad
	downloadIdealLoad(config, config.driveCertificate)
	return ns.load(config.idealshifts).keys()

def getVacations(config, sandbox):
	from tomatic.retriever import downloadVacations
	downloadVacations(config, 'odoo')

@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
	u'Manages busy hours that persons cannot be attending phone'

@cli.command()
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
def list(date, sandbox, optional, required):
	date = busy.isodate(date)
	sandbox=Path(sandbox)
	config = ns.load('config.yaml')
	config.monday = date
	config.idealshifts = sandbox/'idealshifts.yaml'
	activePersons = getActivePersons(config, sandbox)
	getVacations(config, sandbox)
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
		]
    ))

	out("\n# Detall\n")
	for weekday in busy.weekdays:
		out("\n## {}\n", weekday)
		for hour in range(busy.nturns):
			busyAtTime = reasonTable.get((weekday, hour), {})
			out("\n### {}a hora ({})\n", hour+1, len(busyAtTime))
			for person, reasons in sorted(busyAtTime.items()):
				for reason in reasons:
					out("- {}: {}", person, reason)
@cli.command()
@click.argument('date',
	default=None,
	)
@click.argument('sandbox',
	default='',
	)
def forced_overlap(date, sandbox):
	date = busy.isodate(date)
	sandbox=Path(sandbox)

	config = ns.load('config.yaml')
	config.monday = date
	config.idealshifts = sandbox/'idealshifts.yaml'
	activePersons = getActivePersons(config, sandbox)

	busytable = busy.BusyTable(
		days=busy.weekdays,
		nhours = busy.nturns,
		persons = activePersons,
	)
	for busyfile in [
		'indisponibilitats.conf',
		]:
		busytable.load(format(sandbox/busyfile), date)

	reasonTable = busytable.explain()

	forced_turns = ns.load('data/forced-turns.yaml').timetable

	out("\n# Indisponibilitats permaments no opcionals que es solapen amb torns forçats\n")

	for weekday, hours in forced_turns.items():
		for hour, lines in enumerate(hours):
			for person in lines:
				if person not in activePersons:
					print(weekday, hour, person, "No te carrega ideal")
					continue
				reason = busytable.isBusy(weekday, hour, person)
				if not reason: continue
				print(weekday, config.hours[hour], person, reason)


if __name__=='__main__':
	cli()


