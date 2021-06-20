#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import click
from consolemsg import warn, step
from tomatic.tomatic_websockets import WebSocketTomaticServer
from tomatic.api import app, pbx, schedules
from tomatic.pbxqueue import PbxQueue
from tomatic import __version__

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
@click.option('--queue', '-q',
    type=int,
    default=None,
    help="Override pbx queue configured in configuration",
    )
@click.option('--printrules',
    is_flag=True,
    help="Prints the url patterns being serverd",
    )
@click.option('--ring',
    is_flag=True,
    help="Listen incommings calls",
    )
@click.option('--date', '-d',
    help="Data a simular en comptes d'avui"
    )
@click.option('--time','-t',
    default=None,
    help="Hora del dia a simular en comptes d'ara"
    )

def main(fake, debug, host, port, printrules, ring, date, time, queue):
    "Runs the Tomatic web and API"
    print(fake, debug, host, port, printrules, ring, date, time)
    if fake:
        warn("Using fake pbx")
        from tomatic.asteriskfake import AsteriskFake
        p = pbx(AsteriskFake(), 'somenergia')
        initialQueue = schedules.queueScheduledFor(now(date,time))
        p.setQueue(initialQueue)
    else:
        warn("Using real pbx")
        import dbconfig
        from tomatic.pbxareavoip import AreaVoip
        pbx(AreaVoip(), queue or dbconfig.tomatic.areavoip.queue)

        #from tomatic.dbasterisk import DbAsterisk
        #pbx(
        #    DbAsterisk(
        #        dbconfig.tomatic.storagepath,
        #        *dbconfig.tomatic.dbasterisk.args,
        #        **dbconfig.tomatic.dbasterisk.kwds),
        #   "somenergia")

    if printrules:
        for rule in app.routes:
            print(rule.path)

    if ring:
        step("Starting WS thread")
        app.sessionBackChannel = WebSocketTomaticServer()
        app.sessionBackChannel.startCallInfoWS(host=host)
    step("Starting API")
    for rule in app.routes:
        step("- {}", rule.path)
    import uvicorn
    uvicorn.run("tomatic.api:app", debug=debug, host=host, port=port, reload=debug)
    step("API stopped")
    if ring:
        app.sessionBackChannel.stopCallInfoWS()
        step("WS thread stopped")

if __name__=='__main__':
    main()

