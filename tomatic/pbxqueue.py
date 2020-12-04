# -*- coding: utf-8 -*-

from yamlns import namespace as ns
import datetime

from .schedulestorage import Storage
from .dbasterisk import DbAsterisk
from .scheduling import choosers, Scheduling
from .remote import Remote
from . import persons

import dbconfig

class PbxQueue(object):

    def __init__(self, pbx, queue='somenergia'):
        self._queue = queue
        self.backend = pbx

    def setQueue(self, names):
        self.backend.setQueue(self._queue, names)

    def queue(self):
        return self.backend.queue(self._queue)
    
    def pause(self, name):
        self.backend.pause(self._queue, name)

    def resume(self, name):
        self.backend.resume(self._queue, name)

    def add(self, name):
        self.backend.add(self._queue, name)



# vim: ts=4 sw=4 et
