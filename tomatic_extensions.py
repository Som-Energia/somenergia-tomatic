#!/usr/bin/env python

import dbconfig
import click
from yamlns import namespace as ns

from tomatic import __version__
from tomatic import persons
from tomatic.dbasterisk import DbAsterisk

def table(data):
	return u'\n'.join(u'\t'.join(type(u'')(c) for c in row) for row in data)

def initBackend():
	return DbAsterisk(
		*dbconfig.tomatic.dbasterisk.args,
		**dbconfig.tomatic.dbasterisk.kwds
	)

@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
	'Manages Asterisk extensions based on Tomatic configuration'

@cli.command()
def show():
	"Shows current queue status"
	backend = initBackend()
	click.echo(table(backend.extensions()))

@cli.command()
def clear():
	"Clears the queue"
	backend = initBackend()
	backend.clearExtensions()

@cli.command()
@click.argument('extension')
@click.argument('fullname')
def add(extension, fullname):
	"Adds a new extension"
	backend = initBackend()
	backend.addExtension(extension,fullname)

@cli.command()
@click.argument('extension')
def remove(extension):
	"Removes the extension"
	backend = initBackend()
	backend.removeExtension(extension)


@cli.command()
def load():
	backend = initBackend()
	backend.clearExtensions()
	for name, extension in persons.persons().extensions.values():
		backend.addExtension(
			type(u'')(extension),
			persons.nameByExtension(extension),
		)

if __name__=='__main__':
	cli()


