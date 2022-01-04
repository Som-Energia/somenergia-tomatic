#!/usr/bin/env python

import dbconfig
import click
from yamlns import namespace as ns

from tomatic import __version__
from tomatic import persons
from tomatic.pbx import pbxcreate, pbxtypes

def table(data):
	return u'\n'.join(u'\t'.join(type(u'')(c) for c in row) for row in data)

backend_option = click.option('--backend', '-b',
    type=click.Choice(pbxtypes),
    help="PBX backend to use",
    callback=(lambda ctx, param, value: pbxcreate(value)),
)

@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
	'Manages Asterisk extensions based on Tomatic configuration'

@cli.command()
@backend_option
def show(backend):
	"Shows current queue status"
	click.echo(table(backend.extensions()))

@cli.command()
@backend_option
def clear(backend):
	"Clears the queue"
	backend.clearExtensions()

@cli.command()
@backend_option
@click.argument('extension')
@click.argument('fullname')
@click.argument('email', default='')
def add(backend, extension, fullname, email=''):
	"Adds a new extension"
	backend.addExtension(extension,fullname)

@cli.command()
@backend_option
@click.argument('extension')
def remove(backend, extension):
	"Removes the extension"
	backend.removeExtension(extension)


@cli.command()
@backend_option
def load(backend):
	backend.clearExtensions()
	for id, extension in persons.persons().extensions.items():
		backend.addExtension(
			type(u'')(extension),
			persons.nameByExtension(extension),
			persons.persons().emails.get(id, ''),
		)

if __name__=='__main__':
	cli()

# vim: ts=4 sw=4 et
