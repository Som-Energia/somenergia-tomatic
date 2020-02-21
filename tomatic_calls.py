#!/usr/bin/env python
from __future__ import print_function
from consolemsg import step, u
from datetime import datetime
from pony.orm import (
    PrimaryKey,
    Database,
    Required,
    Optional,
    sql_debug,
    select,
    delete,
    db_session,
    sum as ag_sum,
    count as ag_count,
)
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import os
srcpath = os.path.dirname(os.path.abspath(__file__))
yamlconfigpath = os.path.join(srcpath,'persons.yaml')

from yamlns import namespace as ns
import dbconfig
args = dbconfig.tomatic.dbasterisk
db=Database()
db.bind(*args.args, **args.kwds)

import click

from tomatic import __version__

@click.group()
@click.help_option()
@click.version_option(__version__)
def cli():
    'Extract information from the Asterisk call log'


class Calls(db.Entity):
    _table_ = 'cdr'
    calldate = Required(datetime, index=True)
    clid = Required(str, 80)
    src = Required(str, 80)
    dst = Required(str, 80, index=True)
    dcontext = Required(str, 80)
    channel = Required(str, 80)
    dstchannel = Required(str, 80)
    lastapp = Required(str, 80)
    lastdata = Required(str, 80)
    duration = Required(int) # size 11
    billsec = Required(int) # size 11
    disposition = Required(str, 45)
    amaflags = Required(int) # size 11
    accountcode = Required(str, 20, index=True)
    userfield = Required(str, 255)
    uniqueid = PrimaryKey(str, 32)
    #linkedid = Required(str, 32)
    #sequence = Required(str, 32)
    #peeraccount = Required(str, 32)

db.generate_mapping(create_tables=False)

date_option = click.option('--date', '-d',
    help="Data a simular en comptes d'avui"
    )

def dateOrToday(date=None):
    from yamlns.dateutils import Date
    import datetime
    if date is None:
        return datetime.date.today()
    date = Date(date)
    return datetime.datetime(*date.timetuple()[:3])

def properNameByExtension(config, extension):
    extensions2names = dict(t[::-1] for t in config.extensions.items())
    name = extensions2names.get(extension,extension)
    names = config.get('names',{})
    if name in names:
        return names[name]
    return name.title()

@cli.command()
def dumpschema():
    "Dumps the db schema, for debug purposes"
    with db_session():
        for x in db.execute("show create table cdr"): print(x[1])


@cli.command()
@date_option
def summary(date):
    adate = dateOrToday(date)
    step("Trucades ateses")
    with db_session():
        calls = select((
            c.dstchannel[4:8],
            ag_count(c.duration),
            ag_sum(c.billsec),
            c.clid,
            c.lastapp,
            c.lastdata,
            c.disposition,
            )
            for c in Calls
            if c.calldate.date() == adate
            and c.dst=='s'
            ).order_by(-3)
        print('\t'.join('trucades minuts extensio '.split()))
        for call in calls:
            extension, trucades, segons, callid, lastapp, lastdata, disposition = call
            minuts="{:02}:{:02} min".format(*divmod(segons,60))
            lastdata = ''.join(lastdata.split('/')[-1:])
            #if len(extension)!=4: continue
            if extension:
                config = ns.load(yamlconfigpath)
                header = u"{} {}".format(extension, properNameByExtension(config, extension))
            elif lastapp == 'Hangup':
                header = lastapp
            elif lastapp == 'Playback':
                header = ''.join(lastdata.split('/')[-1:])
            elif disposition in ('NO ANSWER', 'BUSY'):
                header = disposition
            else:
                header = '???'
            print('\t'.join([
                u(trucades), minuts, header
                ]))
@cli.command()
@date_option
def all(date):
    """Prints all the registers for the day"""
    adate = dateOrToday(date)
    with db_session():
        for x in db.execute("select * from cdr where date(calldate)=$adate order by calldate"):
            print(u'\t'.join(u(a) for a in x))

@cli.command()
@date_option
def unanswered(date):
    adate = dateOrToday(date)
    step("trucades no servides")
    with db_session():
        for x in db.execute("select * from cdr where dstchannel='' and dst='s' and date(calldate)=$adate order by calldate"):
            print('\t'.join(u(a) for a in x))


    with db_session():
        for c in select(((
                ag_count(c),
                c.disposition,
                c.lastapp,
                c.lastdata,
                )
                for c in Calls
                if c.dstchannel==''
                and c.dst=='s'
                and c.calldate.date()==adate
        )).order_by("c.calldate"):
            n, disposition, lastapp, lastdata = c
            if lastapp == 'Hangup':
                print("Penjades:", n)
                continue
            if lastapp == 'Playback':
                print("Contestador {}: {}".format(''.join(lastdata.split('/')[-1:]), n))
                continue
            if disposition == 'NO ANSWER':
                print("Sense resposta:", n)
                continue
            if disposition == 'BUSY':
                print("Ocupades:", n)
                continue
            print(c)


@cli.command()
@date_option
def missed(date):
    adate = dateOrToday(date)
    step("Trucades perdudes")
    with db_session():
        print('\t'.join('origen n'.split()))
        for x in select((
            c.src,
            c.dcontext,
            c.lastapp,
            c.lastdata,
            ag_count(c),
            )
            for c in Calls
            if c.calldate.date() == adate
            and c.dcontext == 'atencio'
            and c.lastdata == '/var/lib/asterisk/sounds/custom/liniesocupades'
        ):
            print('\t'.join(u(s) for s in x))


if __name__=='__main__':
    #sql_debug(True)
    cli()


# vim: et ts=4 sw=4
