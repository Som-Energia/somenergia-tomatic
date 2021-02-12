#!/usr/bin/env python
# -*- encoding: utf8 -*-


from tomatic.dbasterisk import DbAsterisk
from tomatic.pbxareavoip import AreaVoip
from tomatic.schedulestorage import Storage
from tomatic.scheduling import choosers, Scheduling
from tomatic.remote import Remote
from tomatic.persons import extension
from consolemsg import u, step, out
import dbconfig
import sys
import os
import click
from tomatic import __version__
from yamlns import namespace as ns

def table(data):
	return '\n'.join('\t'.join(u(c) for c in row) for row in data)


queue_option = click.option('--queue', '-q',
	default=dbconfig.tomatic.areavoip.queue,
	help="nom de la cua"
	)
members_option = click.option('--member', '-m',
	multiple=True,
	help="selects members"
	)
date_option = click.option('--date', '-d',
	help="Data a simular en comptes d'avui"
	)
time_option = click.option('--time','-t',
	default=None,
	help="Hora del dia a simular en comptes d'ara"
	)

def now(date, time):
	from yamlns.dateutils import Date
	import datetime
	now = datetime.datetime.now()
	return datetime.datetime.combine(
		now.date() if date is None else Date(date),
		now.time() if time is None else datetime.time(*[int(x) for x in(time.split(":"))])
		)

def pbx():
    return AreaVoip()
    return DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)


@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
	'Manages Asterisk realtime queues based on Tomatic schedules'

@cli.command()
@queue_option
def show(queue):
	"Shows current queue status"
	db = pbx()
	rows = db.queue(queue)
	if rows:
		keys = list(rows[0].keys())
		click.echo(table([keys] + [[row[key] for key in keys] for row in rows]))


@cli.command()
@queue_option
def clear(queue):
	"Clears the queue"
	db = pbx()
	db.setQueue(queue, [])

@cli.command()
@queue_option
@members_option
def pause(queue,member):
	"Pauses a set of members"
	db = pbx()
	for amember in member:
		db.pause(queue,amember)

@cli.command()
@queue_option
@members_option
def resume(queue,member):
	"Resumes a set of members"
	db = pbx()
	for amember in member:
		db.resume(queue,amember)

@cli.command()
@queue_option
@members_option
def add(queue,member):
	"Resumes a set of members"
	db = pbx()
	for amember in member:
		db.add(queue,amember)

@cli.command()
@queue_option
@date_option
@time_option
def set(queue, date, time):
	"Sets the queue according Tomatic's schedule"
	storage = Storage(dbconfig.tomatic.storagepath)
	members = storage.queueScheduledFor(now(date,time))
	db = pbx()
	db.setQueue(queue, members)

@cli.command()
@queue_option
@date_option
@time_option
def preview(queue, date, time):
	"Tells the queue according Tomatic's schedule, does no set"
	storage = Storage(dbconfig.tomatic.storagepath)
	members = storage.queueScheduledFor(now(date,time))
	click.echo(', '.join((
		name
		for name in members
		if extension(name)
	)))


@cli.command()
@queue_option
@click.option('--yaml',
	is_flag=True,
	help="Use YAML output"
	)
def status(queue, yaml=False):
	"Provisional: returns the queue status command line"
	db = pbx()
	queuepeers = db.queue(queue)

	if yaml:
		click.echo(ns(queue=queuepeers).dump())
		return

	click.echo(80*"=")
	if not queuepeers:
		click.echo(u"No hi ha ningú a la cua")

	for peer in queuepeers:
		click.echo(u'{name} ({extension}) Porta {ncalls} trucades finalitzades. La darrera fa {minutes} minuts. {disconnected}{paused}{incall}{available}{ringing}{flags} '.format(
			**dict(peer,
				minutes = peer.secondsSinceLastCall//60,
				disconnected = " [DESCONECTAT!!]" if peer.disconnected else "",
				paused = " [PAUSAT]" if peer.paused else "",
				incall = " [Trucada en curs]" if peer.incall else "",
				ringing = " [Ring]" if peer.ringing else "",
				available = " [Comunica]" if not peer.available and not peer.incall and not peer.ringing else "",
				flags = u''.join(u" {{{}}}".format(u(flag)) for flag in peer.flags),
			)
		))
	click.echo(80*"=")





if __name__=='__main__':
	cli()


