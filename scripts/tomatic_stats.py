#!/usr/bin/env python3


from yamlns import ns
from consolemsg import step, error, success
from pathlib import Path
import datetime
import pytz
#import configdb
#queue=configdb.tomatic.irontec.queue
queue='atencio_client'

localtz=pytz.timezone('Europe/Madrid')

def p(x): print(x); return x

dates = [
    datetime.datetime.fromtimestamp(
        call['@calldate']/1000,
        tz=localtz,
    )
    for calllogyaml in sorted(Path('old-calls').glob('calls-*.yaml'))
    for call in ns.load(calllogyaml).calls
    if call.get('call_type') == 'entrante'
    and call.get('queuename')==queue
]

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
plt.savefig('call-weekly-frequency.pdf')

