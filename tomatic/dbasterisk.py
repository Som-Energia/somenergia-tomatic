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
)

class DbAsterisk(object):

    def __init__(self, *args, **kwds):
        db = Database()
        class QueueMemberTable(db.Entity):
            _table_ = 'queue_members'
            uniqueid = PrimaryKey(int, auto=True)
            membername = Optional(str) #, size=40)
            queue_name = Optional(str) #, size=128)
            interface =  Optional(str) #, size=128)
            penalty = Optional(int) #, size=11)
            paused =  Optional(int) #, size=11)
            # UNIQUE KEY queue_interface (queue_name, interface)
        #sql_debug(True)

        db.bind(*args, **kwds)
        db.generate_mapping(create_tables=True)
        self._queueMembers = QueueMemberTable

    @db_session
    def setQueue(self, queue, extensions):
        delete(
            m for m in self._queueMembers
            if m.queue_name == queue
            )
        for extension in extensions:
            self.add(queue, extension)

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
                )
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
        self._queueMembers(
            membername='SIP/{}@bustia_veu'.format(extension),
            queue_name=queue,
            interface='SIP/{}'.format(extension),
            penalty=None,
            paused=False,
        )

# vim: ts=4 sw=4 et
