#!/usr/bin/env python

from tomatic.dbasterisk import DbAsterisk
import dbconfig
import sys
import click
from yamlns import namespace as ns
from tomatic import __version__
from pathlib2 import Path

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


def properName(persons, name):
	names = persons.get('names',{})
	if name in names:
		return names[name]
	return name.title()


@cli.command()
def load():
	db = DbAsterisk(*dbconfig.tomatic.dbasterisk.args,**dbconfig.tomatic.dbasterisk.kwds)
	persons = ns()
	for config in ['config.yaml', 'persons.yaml']:
		if Path(config).exists():
			persons.update(ns.load(config))
	db.clearExtensions()
	for name, extension in persons.extensions.iteritems():
		db.addExtension(
			unicode(extension),
			properName(persons, name)
			)



if __name__=='__main__':
	cli()


