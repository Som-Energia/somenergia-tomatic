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
plt.savefig(sys.argv[1] if len(sys.argv)>1 else 'call-weekly-frequency.pdf')

