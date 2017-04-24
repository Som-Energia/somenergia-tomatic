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

    def __init__(self, *args):
        db = Database()
        class QueueMemberTable(db.Entity):
            uniqueid = PrimaryKey(int, auto=True)
            membername = Optional(str) #, size=40)
            queue_name = Optional(str) #, size=128)
            interface =  Optional(str) #, size=128)
            penalty = Optional(int) #, size=11)
            paused =  Optional(int) #, size=11)
            # UNIQUE KEY queue_interface (queue_name, interface)
        sql_debug(True)
        db.bind(*args, create_db=True)
        db.generate_mapping(create_tables=True)
        self._queueMembers = QueueMemberTable

    @db_session
    def setQueue(self, extensions):
        delete( m for m in self._queueMembers)
        for extension in extensions:
            self._queueMembers(
                membername='SIP/{}@bustia_veu'.format(extension),
                queue_name='callcenter_somenergia',
                interface='SIP/{}'.format(extension),
                penalty=None,
                paused=False,
            )

    @db_session
    def currentQueue(self):
        return [(
            m.interface.split('/')[-1],
            False,
            )
            for m in select(q for q in self._queueMembers)
            ]
 

# vim: ts=4 sw=4 et
