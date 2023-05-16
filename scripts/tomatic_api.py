#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import click
from consolemsg import warn, step
from tomatic.api import app, schedules
from tomatic import __version__
from tomatic.pbx import pbxqueue, pbxtypes
import os

def now(date, time):
    from yamlns.dateutils import Date
    import datetime
    now = datetime.datetime.now()
    return datetime.datetime.combine(
        now.date() if date is None else Date(date),
        now.time() if time is None else datetime.time(*[int(x) for x in(time.split(":"))])
        )

@click.command()
@click.help_option()
@click.version_option(__version__)

@click.option('--fake',
    is_flag=True,
    help="Use the true pbx instead the fake one",
    )
@click.option('--debug',
    is_flag=True,
    help="Runs in debug mode",
    )
@click.option('--host', '-h',
    default='0.0.0.0',
    help="The address to listen to",
    )
@click.option('--port', '-p',
    type=int,
    default=4555,
    help="The port to listen to",
    )
@click.option('--backend', '-b',
    default=None,
    type=click.Choice(pbxtypes),
    help="Override pbx backend configured in configuration",
    )
@click.option('--queue', '-q',
    default=None,
    help="Override pbx queue configured in configuration",
    )
@click.option('--printrules',
    is_flag=True,
    help="Prints the url patterns being serverd",
    )
@click.option('--date', '-d',
    help="Data a simular en comptes d'avui"
    )
@click.option('--time','-t',
    default=None,
    help="Hora del dia a simular en comptes d'ara"
    )
@click.option('--variant',
    default=None,
    type=click.Choice(['tomatic', 'pebrotic', 'ketchup']),
    help="Identify the instance as this variant",
    )

def main(fake, debug, host, port, printrules, date, time, backend, queue, variant):
    "Runs the Tomatic web and API"
    print(fake, debug, host, port, printrules, date, time, backend, queue, variant)

    if printrules:
        for rule in app.routes:
            print(rule.path)

    p = pbxqueue('fake' if fake else backend, queue)

    if not fake and backend!='fake':
        warn(f"Using real pbx: {backend}")
    else:
        warn("Using fake pbx")
        initialQueue = schedules.queueScheduledFor(now(date,time))
        p.setQueue(initialQueue)

    if variant:
        os.environ["TOMATIC_VARIANT"] = variant

    step("Starting API")
    if printrules:
        for rule in app.routes:
            step("- {}", rule.path)
    import uvicorn
    uvicorn.run("tomatic.api:app", host=host, port=port, reload=debug)
    step("API stopped")

if __name__=='__main__':
    main()

