#!/usr/bin/env python
# -*- encoding: utf8 -*-


from tomatic.schedulestorage import Storage
from tomatic.persons import extension
from tomatic.directmessage import send
from tomatic.pbx import pbxqueue, pbxtypes
from consolemsg import u
import dbconfig
import click
from tomatic import __version__
from yamlns import namespace as ns

def table(data):
    return '\n'.join('\t'.join(u(c) for c in row) for row in data)


backend_option = click.option('--backend', '-b',
    default=dbconfig.tomatic.get('pbx',None) or 'areavoip',
    type=click.Choice(pbxtypes),
    help="PBX backend to use",
)
queue_option = click.option('--queue', '-q',
    default=None,
    help="nom de la cua"
)
members_option = click.option('--member', '-m',
    multiple=True,
    help="selects members"
)
date_option = click.option('--date', '-d',
    help="Data a simular en comptes d'avui"
)
time_option = click.option('--time','-t',
    default=None,
    help="Hora del dia a simular en comptes d'ara"
)

def now(date, time):
    from yamlns.dateutils import Date
    import datetime
    now = datetime.datetime.now()
    return datetime.datetime.combine(
        now.date() if date is None else Date(date),
        now.time() if time is None else datetime.time(*[int(x) for x in(time.split(":"))])
        )

@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
    'Manages Asterisk realtime queues based on Tomatic schedules'

@cli.command()
@backend_option
@queue_option
def show(backend, queue):
    "Shows current queue status"
    pbx = pbxqueue(backend, queue)
    rows = pbx.queue()
    if rows:
        keys = list(rows[0].keys())
        click.echo(table([keys] + [[row[key] for key in keys] for row in rows]))


@cli.command()
@backend_option
@queue_option
def clear(backend, queue):
    "Clears the queue"
    pbx = pbxqueue(backend, queue)
    pbx.setQueue([])

@cli.command()
@backend_option
@queue_option
@members_option
def pause(backend, queue, member):
    "Pauses a set of members"
    pbx = pbxqueue(backend, queue)
    for amember in member:
        pbx.pause(amember)

@cli.command()
@backend_option
@queue_option
@members_option
def resume(backend, queue, member):
    "Resumes a set of members"
    pbx = pbxqueue(backend, queue)
    for amember in member:
        pbx.resume(amember)

@cli.command()
@backend_option
@queue_option
@members_option
def add(backend, queue, member):
    "Resumes a set of members"
    pbx = pbxqueue(backend, queue)
    for amember in member:
        pbx.add(amember)

@cli.command()
@backend_option
@queue_option
@date_option
@time_option
def set(backend, queue, date, time):
    "Sets the queue according Tomatic's schedule"
    pbx = pbxqueue(backend, queue)
    storage = Storage(dbconfig.tomatic.storagepath)
    members = storage.queueScheduledFor(now(date, time))
    pbx.setQueue(members)

@cli.command()
@date_option
@time_option
def preview(date, time):
    "Tells the queue according Tomatic's schedule, does no set"
    storage = Storage(dbconfig.tomatic.storagepath)
    members = storage.queueScheduledFor(now(date, time))
    click.echo(', '.join((
        name
        for name in members
        if extension(name)
    )))


@cli.command()
@backend_option
@queue_option
@click.option('--yaml',
    is_flag=True,
    help="Use YAML output"
    )
def status(backend, queue, yaml=False):
    "Provisional: returns the queue status command line"
    pbx = pbxqueue(backend, queue)
    queuepeers = pbx.queue()

    if yaml:
        click.echo(ns(queue=queuepeers).dump())
        return

    click.echo(80*"=")
    if not queuepeers:
        click.echo(u"No hi ha ningú a la cua")

    for peer in queuepeers:
        click.echo(
            u'{name} ({extension}) Porta {ncalls} trucades finalitzades. '
            u'Les ha atés en {callminutes}:{callseconds} minuts. '
            u'La darrera fa {minutes}:{seconds:02} minuts. '
            '{disconnected}{paused}{incall}{available}{ringing}{flags} '.format(
            **dict(peer,
                callminutes = peer.secondsInCalls//60,
                callseconds = peer.secondsInCalls%60,
                minutes = peer.secondsSinceLastCall//60,
                seconds = peer.secondsSinceLastCall%60,
                disconnected = " [DESCONECTAT!!]" if peer.disconnected else "",
                paused = " [PAUSAT]" if peer.paused else "",
                incall = " [Trucada en curs]" if peer.incall else "",
                ringing = " [Ring]" if peer.ringing else "",
                available = " [Comunica]" if not peer.available and not peer.incall and not peer.ringing else "",
                flags = u''.join(u" {{{}}}".format(u(flag)) for flag in peer.flags),
            )
        ))
    click.echo(80*"=")


@cli.command()
@backend_option
@queue_option
def monitor(backend, queue):
    """Warns if an agent gets disconnected"""

    def disconnected(agents):
        return {
            agent.key
            for agent in agents
            if agent.disconnected and not agent.paused
        }

    try:
        previous = ns.load('monitor.yaml').queue
    except:
        previous = []

    pbx = pbxqueue(backend, queue)
    current = pbx.queue()

    newDisconnected = disconnected(current) - disconnected(previous)

    if newDisconnected:
        print("Compte: agents desconectades: {}".format(', '.join(list(newDisconnected))))
        if dbconfig.tomatic.get('monitorChatChannel', None):
            send(dbconfig.tomatic.monitorChatChannel,
                "Compte: agents desconectades: {}".format(', '.join(list(newDisconnected))))

    # Store the current for the next monitoring
    ns(queue=current).dump('monitor.yaml')





if __name__=='__main__':
    cli()


# vim: ts=4 sw=4 et
