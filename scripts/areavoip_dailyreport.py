#!/usr/bin/env python
# -*- encoding: utf8 -*-
import datetime
from consolemsg import u, step, out
import dbconfig
import sys
import os
import click
from tomatic import __version__
from yamlns import namespace as ns
from pathlib import Path
from emili import sendMail


template = """\
<style>
tr {{ margin: 2px; background: #eee; }}
</style>

Hola Supers,

Us faig arribar les estadístiques dels torns d'avui.

- Total de trucades rebudes: {CALLSRECEIVED}
- Trucades contestades: {ANSWEREDCALLS}
- Trucades abandonades abans de contestar: {ABANDONEDCALLS}
- Trucades perdudes: {TIMEDOUTCALLS}

Temps de trucada:

- Agregat: {TALKTIME}
- Mitjana: {AVERAGETALKTIME}

Temps d'espera:

- Agregat: {HOLDTIME}
- Mitjana: {AVERAGEHOLDTIME}
- Màxim: {MAXHOLDTIME}

<table>
<tr>
<th>Rebudes</th>
<th>Contestades</th>
<th>Abandonades</th>
<th>Perdudes</th>
</tr>
<tr>
<td>{CALLSRECEIVED}</td>
<td>{ANSWEREDCALLS}</td>
<td>{ABANDONEDCALLS}</td>
<td>{TIMEDOUTCALLS}</td>
</tr>
</table>

<table>
<tr>
<th colspan=2>Temps de trucada</th>
<th colspan=3>Temps d'espera</th>
</tr>
<tr>
<th>Total</th>
<th>Mijtà</th>
<th>Total</th>
<th>Mitjà</th>
<th>Màxim</th>
</tr>
<tr>
<td>{TALKTIME}</td>
<td>{AVERAGETALKTIME}</td>
<td>{HOLDTIME}</td>
<td>{AVERAGEHOLDTIME}</td>
<td>{MAXHOLDTIME}</td>
</tr>
</table>
"""
import dbconfig

fields = [
    'DATE',
    'CALLSRECEIVED',
    'ANSWEREDCALLS',
    'ABANDONEDCALLS',
    'TIMEDOUTCALLS',
    'TALKTIME',
    'AVERAGETALKTIME',
    'HOLDTIME',
    'AVERAGEHOLDTIME',
    'MAXHOLDTIME',
]

def cli():
    from tomatic.pbx.pbxareavoip import AreaVoip;
    pbx = AreaVoip()
    stats = ns(
        pbx._api('INFO',
            info='queue',
            id=dbconfig.tomatic.areavoip.queue,
            format='json',
        ),
        DATE='{:%Y-%m-%d}'.format(datetime.date.today()),
    )

    statsfile = Path('stats.csv')
    if not statsfile.exists():
        statsfile.write_text('\t'.join(fields) + '\n', encoding='utf8')
    with statsfile.open(mode='a', encoding='utf8') as csv:
        csv.write('\t'.join(str(stats[field]) for field in fields) + '\n')

    sendMail(
        sender=dbconfig.tomatic.dailystats.sender,
        to=dbconfig.tomatic.dailystats.recipients,
        subject="Informe diari de trucades - {DATE}".format(**stats),
        md=template.format(**stats),
        config='dbconfig.py',
        verbose=True,
    )




if __name__=='__main__':
    cli()


