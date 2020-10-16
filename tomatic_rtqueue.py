#!/usr/bin/env python

from tomatic.dbasterisk import DbAsterisk
from tomatic.schedulestorage import Storage
from tomatic.scheduling import choosers, Scheduling
from tomatic.remote import Remote
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


def nameByExtension(extension):
	if not hasattr(nameByExtension, 'extensions2names'):
		srcpath = os.path.dirname(os.path.abspath(__file__))
		yamlconfigpath = os.path.join(srcpath,'persons.yaml')
		config = ns.load(yamlconfigpath)
		nameByExtension.names = config.names
		nameByExtension.extensions2names = dict(
			(e,n) for n,e in config.extensions.items()
		)
	name = nameByExtension.extensions2names.get(extension,extension)
	if name in nameByExtension.names:
		return nameByExtension.names[name]
	return name.title()

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

@cli.command()
@queue_option
def status(queue):
	"Provisional: returns the queue status command line"

	step("Connectant a la centraleta")

	sortida="""\
somenergia has 0 calls (max unlimited) in 'leastrecent' strategy (4s holdtime, 340s talktime), W:0, C:159, A:88, SL:100.0% within 30s
   Members: 
      SIP/3063@bustia_veu (SIP/3063) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 181 secs ago)
      SIP/3188@bustia_veu (SIP/3188) (ringinuse disabled) (realtime) (in call) (In use) has taken 3 calls (last was 630 secs ago)
      SIP/3043@bustia_veu (SIP/3043) (ringinuse disabled) (realtime) (Not in use) has taken 4 calls (last was 257 secs ago)
      SIP/3084@bustia_veu (SIP/3084) (ringinuse disabled) (realtime) (Not in use) has taken 6 calls (last was 187 secs ago)
      SIP/2905@bustia_veu (SIP/2905) (ringinuse disabled) (realtime) (in call) (In use) has taken 5 calls (last was 564 secs ago)
      SIP/3048@bustia_veu (SIP/3048) (ringinuse disabled) (realtime) (Not in use) has taken 4 calls (last was 189 secs ago)
      SIP/2902@bustia_veu (SIP/2902) (ringinuse disabled) (realtime) (in call) (In use) has taken 2 calls (last was 1367 secs ago)
   No Callers
"""
	remote = Remote(**dbconfig.tomatic.ssh)
	sortida = remote.run("asterisk -rx 'queue show {}'".format(queue))

	def extract(pattern, string, default=None):
		import re
		matches = re.search(pattern, string)
		return matches.group(1) if matches else default

	def extractQueuepeerInfo(line):
		peer = ns()
		peer.extension = extract('\(SIP/([0-9]+)\)', line, '????')
		peer.name = nameByExtension(peer.extension)
		peer.paused = '(paused)' in line
		peer.disconnected = '(Unavailable)' in line
		peer.available = '(Not in use)' in line
		peer.incall = '(in call)' in line
		peer.ncalls = int(extract('has taken ([0-9]+) calls', line, '0'))
		peer.secondsSinceLastCall = int(extract('last was ([0-9]+) secs ago', line, '0'))
		import re
		peer.flags = [ flag
			for flag in re.findall(r"\(([^)]+)\)",line)
			if flag not in [
				'Not in use',
				'In use', # ignored, expected to be negated of 'Not in use'
				'in call',
				'Unavailable',
				'paused',
				'realtime', # ignored
				'ringinuse disabled', # ignored
			]
			and not flag.startswith('has taken ')
			and not flag.startswith('last was ')
			and not flag.startswith('SIP/')
		]
		return peer

	queuepeer = [
		extractQueuepeerInfo(line)
		for line in sortida.splitlines()
		if line.strip().startswith('SIP/')
	]
	for peer in queuepeer:
		click.echo('{name} ({extension}) Porta {ncalls} trucades. {disconnected}{paused}{incall}{available}{flags} '.format(
			**dict(peer,
				disconnected = " [DESCONECTAT!!]" if peer.disconnected else "",
				paused = " [PAUSAT]" if peer.paused else "",
				incall = " [En trucada]" if peer.incall else "",
				available = " [Comunica]" if not peer.available and not peer.incall else "",
				flags = ''.join(" {{}}".format(flag) for flag in peer.flags),
			)
		))

	#click.echo(ns(status=queuepeer).dump())
	#click.echo(sortida)
	#sortida = remote.run('''echo 'select callerid, paused, sippeers.* from queue_members join sippeers on queue_members.interface = concat("SIP/", sippeers.name);' | sudo mysql asterisk''')
	#click.echo(sortida)





if __name__=='__main__':
	cli()


