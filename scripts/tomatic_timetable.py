#!/usr/bin/env python

import click
from consolemsg import fail, step
from datetime import datetime, timedelta
from tomatic import schedulestorage

@click.group()
def cli():
    pass


@cli.command()
def retireold():
    schedules = schedulestorage.Storage()
    today = datetime.today()
    twoMondaysAgo = str((today - timedelta(days=today.weekday()+7*2)).date())
    step("Retiring timetables older than {}", twoMondaysAgo)
    schedules.retireOld(twoMondaysAgo)

@cli.command()
@cli.argument(
    'yaml',
    type=Path,
)
def upload():
    schedules = schedulestorage.Storage()
    step("uploading {}".format(yaml))
    graella = ns.load(yaml)
    logmsg = (
        "{}: {} ha pujat {} ".format(
        datetime.now(),
        "tomatic",
        graella.week,
        ))
    graella.setdefault('log',[]).append(logmsg)
    schedules.save(graella)
    schedulestorage.publishStatic(graella)

if __name__=='__main__':
    cli()

