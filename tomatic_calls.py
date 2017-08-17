#!/usr/bin/env python
from consolemsg import step
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
import dbconfig
args = dbconfig.tomatic.dbasterisk
db=Database()
db.bind(*args.args, **args.kwds)

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


def calls():
    return select((
        c.dstchannel[4:8],
        #c.dstchannel[4:8],
        ag_count(c.duration),
        ag_sum(c.billsec),
        c.clid,
        )
        for c in Calls
        if c.calldate.date() == datetime.today().date()
        and c.dst=='s'
        ).order_by(-2)

with db_session():
	for x in db.execute("show create table cdr"): print x[1]

sql_debug(True)
step("trucades no servides")
with db_session():
    today=datetime.today().date()
    for x in db.execute("select * from cdr where dstchannel='' and dst='s' and date(calldate)=$today order by calldate"):
        print '\t'.join(str(a) for a in x)

step("Trucades contestades")
with db_session():
    print '\t'.join('extensio trucades minuts'.split())
    for call in calls():
        extension, trucades, segons, callid = call
        minuts="{:02}:{:02} min".format(*divmod(segons,60))
        #if len(extension)!=4: continue
        print '\t'.join([
            extension, str(trucades), minuts, callid
            ])
step("Trucades perdudes")
with db_session():
    print '\t'.join('origen n'.split())
    for x in select((
        c.src,
        c.dcontext,
        c.lastapp,
        c.lastdata,
        ag_count(c),
        )
        for c in Calls
        if c.calldate.date() == datetime.today().date()
        and c.dcontext == 'atencio'
        and c.lastdata == '/var/lib/asterisk/sounds/custom/liniesocupades'
    ):
        print '\t'.join(str(s) for s in x)


# vim: et ts=4 sw=4
