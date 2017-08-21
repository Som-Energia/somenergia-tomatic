#!/usr/bin/env python

from tomatic.dbasterisk import DbAsterisk
from tomatic.schedulestorage import Storage
from tomatic.scheduling import choosers, Scheduling
import dbconfig
import sys
import click

__version__='1.2.0'

def table(data):
	return '\n'.join('\t'.join(str(c) for c in row) for row in data)


queue_option = click.option('--queue', '-q',
	default='somenergia',
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

@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
	'Manages Asterisk realtime queues based on Tomatic schedules'

@cli.command()
@queue_option
def show(queue):
	"Shows current queue status"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	click.echo(table(db.queue(queue)))


@cli.command()
@queue_option
def clear(queue):
	"Clears the queue"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	db.setQueue(queue, [])

@cli.command()
@queue_option
@members_option
def pause(queue,member):
	"Pauses a set of members"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	for amember in member:
		db.pause(queue,amember)

@cli.command()
@queue_option
@members_option
def resume(queue,member):
	"Resumes a set of members"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	for amember in member:
		db.resume(queue,amember)

@cli.command()
@queue_option
@members_option
def add(queue,member):
	"Resumes a set of members"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	for amember in member:
		db.add(queue,amember)

@cli.command()
@queue_option
@date_option
@time_option
def set(queue, date, time):
	"Sets the queue according Tomatic's schedule"
	week, dow, time = choosers(now(date,time))
	storage = Storage(dbconfig.tomatic.storagepath)
	sched = Scheduling(storage.load(week))
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	db.setQueue(queue, [
		sched.extension(name)
		for name in sched.peekQueue(dow, time)
		if sched.extension(name)
	])

@cli.command()
@queue_option
@date_option
@time_option
def preview(queue, date, time):
	"Tells the queue according Tomatic's schedule, does no set"
	week, dow, time = choosers(now(date,time))
	storage = Storage(dbconfig.tomatic.storagepath)
	sched = Scheduling(storage.load(week))
	click.echo(', '.join((
		name
		for name in sched.peekQueue(dow, time)
		if sched.extension(name)
	)))


if __name__=='__main__':
	cli()


