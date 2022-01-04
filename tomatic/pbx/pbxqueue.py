# -*- coding: utf-8 -*-

class PbxQueue(object):
    """A wrapper for pbx's which allows to assume 
    always the same queue"""

    def __init__(self, pbx, queue=None):
        self._queue = queue or pbx.defaultQueue()
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

    def stats(self, date):
        return self.backend.stats(self._queue, date)



# vim: ts=4 sw=4 et
