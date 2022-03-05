#!/usr/bin/env python
# -*- encoding: utf8 -*-

from consolemsg import u, step, out
import dbconfig
import sys
import os
import click
from tomatic import __version__
from yamlns import namespace as ns

def table(data):
	return '\n'.join('\t'.join(u(c) for c in row) for row in data)

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('request')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def cli(request, args):


    from tomatic.pbx.pbxareavoip import AreaVoip
    pbx = AreaVoip()
    key=None
    kwds={}
    for arg in args:
        if key is None:
            key = arg
            continue
        kwds[key]=arg
        key=None

    click.echo(ns(result=pbx._api(request.upper(), **kwds)).dump())

if __name__=='__main__':
	cli()


