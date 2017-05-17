#!/usr/bin/env python

from tomatic.dbasterisk import DbAsterisk
from tomatic.schedulestorage import Storage
from tomatic.scheduling import choosers, Scheduling
import dbconfig
import sys
import click
from yamlns import namespace as ns

__version__='1.2.0'

def table(data):
	return u'\n'.join(u'\t'.join(unicode(c) for c in row) for row in data)



@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
	'Manages Asterisk extensions based on Tomatic configuration'

@cli.command()
def show():
	"Shows current queue status"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	click.echo(table(db.extensions()))

@cli.command()
def clear():
	"Clears the queue"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	db.clearExtensions()

@cli.command()
@click.argument('extension')
@click.argument('fullname')
def add(extension, fullname):
	"Adds a new extension"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	db.addExtension(extension,fullname)

@cli.command()
@click.argument('extension')
def remove(extension):
	"Removes the extension"
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	db.removeExtension(extension)


def properName(config, name):
	names = config.get('names',{})
	if name in names:
		return names[name]
	return name.title()


@cli.command()
def load():
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	config = ns.load('config.yaml')
	db.clearExtensions()
	for name, extension in config.extensions.iteritems():
		db.addExtension(
			unicode(extension),
			properName(config, name)
			)



if __name__=='__main__':
	cli()


