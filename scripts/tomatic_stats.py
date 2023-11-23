#!/usr/bin/env python3

"""
TODO:
- Date-Hour with 0 calls are not aggregated into the mean
- Horitzontal lines to make the plot more readable
- Nicer x axis labels
"""

from yamlns import ns
from consolemsg import step, error, success, fail
from pathlib import Path
import datetime
import pytz
import sys
import click

@click.group()
def cli(): "Compute several statistics"

@cli.command()
@click.argument('output', metavar="OUTPUT.pdf", default='call-weekly-frequency.pdf')
def weekly_profile(output):
    """
    Outputs a box plot of incomming calls by day of week and hour.
    Ie. for each monday, tuesday, and for each hour,
    which are the mean, quartiles and extremes
    of incoming calls.
    """


    #import configdb
    #queue=configdb.tomatic.irontec.queue
    queue='atencio_client'

    localtz=pytz.timezone('Europe/Madrid')

    stats_dir = Path('stats') # TODO: Take it from configuration

    def p(x): print(x); return x

    dates = [
        datetime.datetime.fromtimestamp(
            call['@calldate']/1000,
            tz=localtz,
        )
        for calllogyaml in sorted(stats_dir.glob('calls-*.yaml'))
        for call in ns.load(calllogyaml).calls
        if call.get('call_type') == 'entrante'
        and call.get('queuename')==queue
    ]

    if not dates:
        fail(f"No stats data found in {stats_dir}")

    import pandas as pd
    import matplotlib.pyplot as plt

    print(len(dates))

    firstdate = min(dates)
    lastdate= max(dates)

    df = pd.DataFrame(dict(datetime=dates))
    # Compute calls every day and hour
    df = df.groupby([
        df['datetime'].dt.date,
        df['datetime'].dt.weekday,
        df['datetime'].dt.hour,
    ]).count()
    df = df.reset_index(names=['date', 'weekday', 'hour'])
    df = df.rename({'datetime': 'calls'}, axis=1)
    del df['date']
    df['weekdayhour']=df['weekday']*100+df['hour']
    del df['weekday']
    del df['hour']
    df = df.plot.box(by='weekdayhour', figsize=(20,10))
    plt.title(f"Calls from {firstdate.date()} to {lastdate.date()}")
    success(f"Generating {output}")
    plt.savefig(output)

@cli.command()
@click.argument('output', metavar="OUTPUT.csv", default='call-usage.csv')
@click.option('--event', 'events', metavar="EVENT", multiple=True, default=[])
@click.option('--from', 'from_', metavar="FROM", type=click.DateTime(formats=['%Y-%m-%d']), default=None)
@click.option('--to', metavar="TO", type=click.DateTime(formats=['%Y-%m-%d']), default=None)
def usage(output, events, from_, to):
    """
    Outputs a csv table containing event count for every user
    """
    import csv
    statsDir = Path('stats/')
    input = statsDir / 'usagelog.log'
    to = to or datetime.datetime.now()

    result = ns()
    with input.open() as f:
        f = csv.reader(f, delimiter='\t')
        for timestamp, event, person in f:
            if events and event not in events:
                warn("filtered by event")
                continue
            if from_ and timestamp < str(from_):
                warn("filtered by from")
                continue
            if to and timestamp > str(to):
                warn("filtered by to")
                continue
            result[person] = result.get(person, 0) + 1

    content = ''.join(
        f"{person}\t{count}\n"
        for count, person in sorted((
            (count, person)
            for person, count in result.items()
        ))
    )
    print(content)
    step(f"Dumpint {output}")
    Path(output).write_text(content)


if __name__ == '__main__':
    cli()

