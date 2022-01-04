#!/usr/bin/env python
# -*- encoding: utf8 -*-
import datetime
import dbconfig
import click
from tomatic import __version__
from tomatic.pbx import pbxqueue, pbxtypes
from pathlib import Path
from emili import sendMail


template = """\
<style>
tr {{ margin: 2px; background: #eee; }}
</style>

Hola Supers,

Us faig arribar les estadístiques dels torns d'avui.

- Total de trucades rebudes: {callsreceived}
- Trucades contestades: {answeredcalls}
- Trucades abandonades abans de contestar: {abandonedcalls}
- Trucades perdudes: {timedoutcalls}

Temps de trucada:

- Agregat: {talktime}
- Mitjana: {averagetalktime}

Temps d'espera:

- Agregat: {holdtime}
- Mitjana: {averageholdtime}
- Màxim: {maxholdtime}

<table>
<tr>
<th>Rebudes</th>
<th>Contestades</th>
<th>Abandonades</th>
<th>Perdudes</th>
</tr>
<tr>
<td>{callsreceived}</td>
<td>{answeredcalls}</td>
<td>{abandonedcalls}</td>
<td>{timedoutcalls}</td>
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
<td>{talktime}</td>
<td>{averagetalktime}</td>
<td>{holdtime}</td>
<td>{averageholdtime}</td>
<td>{maxholdtime}</td>
</tr>
</table>
"""

fields = [
    'date',
    'callsreceived',
    'answeredcalls',
    'abandonedcalls',
    'timedoutcalls',
    'talktime',
    'averagetalktime',
    'holdtime',
    'averageholdtime',
    'maxholdtime',
]

backend_option = click.option('--backend', '-b',
    type=click.Choice(pbxtypes),
    default=dbconfig.tomatic.get('pbx',None) or 'areavoip',
    help="PBX backend to use",
)
queue_option = click.option('--queue', '-q',
    help="nom de la cua"
)
date_option = click.option('--date', '-d',
    help="Data a simular en comptes d'avui"
)

@click.command()
@click.help_option()
@click.version_option(__version__)
@backend_option
@queue_option
@date_option
def cli(backend, queue, date):
    """Sends daily stats of the queue"""

    pbx = pbxqueue(backend, queue)
    date = date or '{:%Y-%m-%d}'.format(datetime.date.today())
    stats = pbx.stats(date=date)

    statsfile = Path('stats.csv')
    if not statsfile.exists():
        statsfile.write_text(
            '\t'.join(fields).upper() + '\n',
            encoding='utf8',
        )
    with statsfile.open(mode='a', encoding='utf8') as csv:
        csv.write('\t'.join(
            str(stats[field])
            for field in fields
        ) + '\n')

    sendMail(
        sender=dbconfig.tomatic.dailystats.sender,
        to=dbconfig.tomatic.dailystats.recipients,
        subject="Informe diari de trucades - {date}".format(**stats),
        md=template.format(**stats),
        config='dbconfig.py',
        verbose=True,
        attachments=[
            'stats.csv',
        ],
    )




if __name__=='__main__':
    cli()


# vim: ts=4 sw=4 et
