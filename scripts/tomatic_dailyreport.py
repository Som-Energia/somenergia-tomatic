#!/usr/bin/env python
# -*- encoding: utf8 -*-
import datetime
from tomatic.config import secrets
import click
from tomatic import __version__
from tomatic.pbx import pbxqueue, pbxtypes
from pathlib import Path
from emili import sendMail
from tomatic.directmessage import send
from yamlns.dateutils import Date

template = """\
<style>
tr {{ margin: 2px; background: #eee; }}
</style>

Hola Supers,

Us faig arribar les estadístiques dels torns d'avui.

- Total de trucades rebudes: {atentioncalls}
- Trucades contestades: {answeredcalls}
- Trucades perdudes: {lostcalls}:
    - Trucades abandonades en espera: {abandonedcalls}
    - Trucades tallades per limit d'espera: {timedoutcalls}
    - Trucades amb la cua d'espera plena: {bouncedcalls}
- Trucades fora d'horari: Mati {earlycalls} / Tarda {latecalls}.

Temps de trucada:

- Agregat: {talktime} s ({talktime_delta})
- Mitjana: {averagetalktime} s ({averagetalktime_delta})

Temps d'espera:

- Agregat: {holdtime} s ({holdtime_delta})
- Mitjana: {averageholdtime} s ({averageholdtime_delta})
- Màxim: {maxholdtime} s ({maxholdtime_delta})

<table>
<tr>
<th>Rebudes</th>
<th>Contestades</th>
<th>Perdudes abandonades</th>
<th>Perdudes timeout</th>
<th>Perdudes cua plena</th>
<th>Matineres</th>
<th>Tardanes</th>
<th>Proves/Partners</th>
</tr>
<tr>
<td>{callsreceived}</td>
<td>{answeredcalls}</td>
<td>{abandonedcalls}</td>
<td>{timedoutcalls}</td>
<td>{bouncedcalls}</td>
<td>{earlycalls}</td>
<td>{latecalls}</td>
<td>{testcalls}</td>
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
    'earlycalls',
    'latecalls',
    'testcalls',
    'bouncedcalls',
]
deltas=[
    'talktime',
    'averagetalktime',
    'holdtime',
    'averageholdtime',
    'maxholdtime',
]

backend_option = click.option('--backend', '-b',
    type=click.Choice(pbxtypes),
    default=secrets('tomatic.pbx','irontec'),
    help="PBX backend to use",
)
queue_option = click.option('--queue', '-q',
    help="nom de la cua"
)
date_option = click.option('--date', '-d',
    help="Data a simular en comptes d'avui"
)
startdate_option = click.option('--start', '-s',
    help="Si s'indica es calcularan totes les dates des d'aquesta fins avui"
)
sendmail_option = click.option('--sendmail',
    is_flag=True,
    help="Si s'indica, s'enviarà un correu a tomatic.dailystats.recipients"
)
sendchat_option = click.option('--sendchat',
    is_flag=True,
    help="Si s'indica, s'enviarà un xat a tomatic.monitorChatChannel",
)
nodump_option = click.option('--nodump',
    is_flag=True,
    help="Si s'indica no afegira linia al fitxer d'estadístiques",
)

def date_range(first, last):
    first = Date(first)
    last = Date(last)
    ndays = (last-first).days + 1
    for d in (
        first + datetime.timedelta(days=i) for i in range(ndays)
    ):
        yield d

@click.command()
@click.help_option()
@click.version_option(__version__)
@backend_option
@queue_option
@date_option
@startdate_option
@sendmail_option
@sendchat_option
@nodump_option
def cli(backend, queue, date, start, sendchat, sendmail, nodump):
    """Sends daily stats of the queue"""

    pbx = pbxqueue(backend, queue)
    date = date or '{:%Y-%m-%d}'.format(datetime.date.today())

    statsfile = Path('stats.csv')
    if not statsfile.exists():
        statsfile.write_text(
            '\t'.join(fields).upper() + '\n',
            encoding='utf8',
        )
    start = start or date
    for d in date_range(start or date, date):
        print(f"d {d}")
        stats = pbx.stats(date=d)
        if nodump: continue
        with statsfile.open(mode='a', encoding='utf8') as csv:
            csv.write('\t'.join(
                str(stats[field])
                for field in fields
            ) + '\n')
    stats.lostcalls = stats.bouncedcalls + stats.timedoutcalls + stats.abandonedcalls
    stats.atentioncalls = stats.callsreceived - stats.testcalls
    if sendmail:
        sendMail(
            sender=secrets('tomatic.dailystats.sender'),
            to=secrets('tomatic.dailystats.recipients'),
            subject="Informe diari de trucades - {date}".format(**stats),
            md=template.format(**dict(
                stats,
                **{
                    delta+'_delta': datetime.timedelta(seconds=stats[delta])
                    for delta in deltas
                },
            )),
            config='dbconfig.py',
            verbose=True,
            attachments=[
                'stats.csv',
            ],
        )
    if sendchat:
        send(secrets('tomatic.monitorChatChannel'),
            "Hola Súpers! Us passem el registre de trucades d'avui! "
            f"Rebudes: {stats['callsreceived'] - stats['latecalls'] - stats['earlycalls'] - stats['testcalls']}. "
            f"Contestades: {stats['answeredcalls']}. "
            f"Perdudes: {stats['lostcalls']}. "
        )





if __name__=='__main__':
    cli()


# vim: ts=4 sw=4 et
