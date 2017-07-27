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
import time

class DbAsterisk(object):

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
    def setQueue(self, queue, extensions):
        delete(
            m for m in self._queueMembers
            if m.queue_name == queue
            )
        for extension in extensions:
            print queue, extension
            self.add(queue, extension)
            # KLUDGE: Let asterisk do its stuff so the wueue gets ordered
            time.sleep(2)

    @db_session
    def queue(self, queue):
        return [(
            m.interface.split('/')[-1],
            m.paused,
            )
            for m in select(
                q for q in self._queueMembers
                if queue is None
                or q.queue_name == queue
                ).order_by("q.uniqueid")
            ]

    @db_session
    def pause(self, queue, extension, paused=True):
        interface = 'SIP/{}'.format(extension)
        member = self._queueMembers.get(
            lambda m: m.interface == interface
                and m.queue_name == queue)
        if member is None: return
        member.paused = paused

    def resume(self, queue, extension):
        self.pause(queue, extension, False)

    @db_session
    def add(self, queue, extension):
        penalty = len(self.queue(queue))
        self._queueMembers(
            membername='SIP/{}@bustia_veu'.format(extension),
            queue_name=queue,
            interface='SIP/{}'.format(extension),
            penalty=penalty,
            paused=False,
        )

    # Extensions

    @db_session
    def addExtension(self, extension, fullname):
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
            )
            ]


# vim: ts=4 sw=4 et
