# -*- coding: utf-8 -*-

from pony.orm import (
    PrimaryKey,
    Database,
    Required,
    Optional,
    sql_debug,
    select,
    delete,
    db_session,
    composite_index,
)
from yamlns import namespace as ns
import time
from .. import persons
from .asteriskcli import queueFromSsh
try:
    import dbconfig
except ImportError:
    dbconfig = None

class DbAsterisk(object):

    defaultQueue = 'somenergia'

    def __init__(self, *args, **kwds):
        db = Database()
        #sql_debug(True)

        class QueueMemberTable(db.Entity):
            _table_ = 'queue_members'
            uniqueid = PrimaryKey(int, auto=True)
            membername = Optional(str, 40)
            queue_name = Optional(str, 128)
            interface =  Optional(str, 128)
            penalty = Optional(int)#, 11)
            paused =  Optional(int)#, 11)
            composite_index(queue_name, interface)

        class SipPeerTable(db.Entity):
            _table_ = 'sippeers'
            id = PrimaryKey(int, auto=True)
            name = Required(str, 10)
            defaultuser = Optional(str, 10)
            context = Optional(str, 40)
            host = Optional(str, 40)
            secret = Optional(str, 40)
            callerid = Optional(str, 40)
            type = Optional(str) #, enum('friend','user','peer')

        #sql_debug(True)
        db.bind(*args, **kwds)
        db.generate_mapping(create_tables=True)
        self._queueMembers = QueueMemberTable
        self._sipPeers = SipPeerTable

    @db_session
    def setQueue(self, queue, names):
        delete(
            m for m in self._queueMembers
            if m.queue_name == queue
            )
        for name in names:
            self.add(queue, name)
            # KLUDGE: Let asterisk do its stuff so the wueue gets ordered
            #time.sleep(1)

    @db_session
    def queue(self, queue):
        if dbconfig and 'ssh' in dbconfig.tomatic:
            return queueFromSsh(queue)

        return [
            ns(
                key = persons.byExtension(extension),
                extension = extension,
                name = persons.name(persons.byExtension(extension)),
                paused = bool(paused),
            )
            for extension, paused
            in self.queueExtensions(queue)
        ]

    @db_session
    def queueExtensions(self, queue):
        return [(
            m.interface.split('/')[-1],
            bool(m.paused),
        )
        for m in select(
            q for q in self._queueMembers
            if queue is None
            or q.queue_name == queue
            ).order_by("q.uniqueid")
        ]

    @db_session
    def pause(self, queue, name, paused=True):
        extension = persons.extension(name)
        interface = 'SIP/{}'.format(extension)
        member = self._queueMembers.get(
            lambda m: m.interface == interface
                and m.queue_name == queue)
        if member is None: return
        member.paused = paused

    def resume(self, queue, name):
        self.pause(queue, name, False)

    @db_session
    def add(self, queue, name):
        extension = persons.extension(name)
        if not extension: return
        self._queueMembers(
            queue_name=queue,
            membername='SIP/{}@bustia_veu'.format(extension),
            interface='SIP/{}'.format(extension),
            penalty=0,
            paused=False,
        )

    # Extensions

    @db_session
    def addExtension(self, extension, fullname, email=''):
        self._sipPeers(
            name = extension,
            defaultuser = extension,
            host = 'dynamic',
            context = 'oficina',
            secret = 'ra{}ra'.format(extension),
            callerid = u'{} <{}>'.format(fullname, extension),
            type = 'friend',
        )

    @db_session
    def clearExtensions(self):
        delete(m for m in self._sipPeers)

    @db_session
    def removeExtension(self,extension):
        delete(
            m for m in self._sipPeers
            if m.name == extension
        )

    @db_session
    def extensions(self):
        return [(
            m.name,
            m.callerid,
            )
            for m in self._sipPeers.select(
                lambda m: True
        )]

# vim: ts=4 sw=4 et
