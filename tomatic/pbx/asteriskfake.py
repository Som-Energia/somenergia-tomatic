# -*- coding: utf-8 -*-

from yamlns import namespace as ns
from .. import persons

class AsteriskFake(object):
    ''

    @staticmethod
    def defaultQueue():
        return 'somenergia'

    def __init__(self):
        self._queuepaused = dict()
        self._queueagents = dict()
        self._extensions = list()

    def _agents(self, queue):
        return self._queueagents.setdefault(queue, list())

    def _paused(self, queue):
        return self._queuepaused.setdefault(queue, set())

    def setQueue(self, queue, persons):
        """Sets persons as current agents of the queue, removing previous ones"""
        self._queueagents[queue] = list()
        self._queuepaused[queue] = set()
        for person in persons:
            self.add(queue, person)

    def add(self, queue, name):
        """Add person as next agent of the queue"""

        extension = persons.extension(name)
        if not extension: return
        self._agents(queue).append(name)

    def queue(self, queue):
        """Returns information of the current agents in the queue"""
        import datetime
        minute = datetime.datetime.now().minute
        return [
            ns(
                key = who,
                paused = who in self._paused(queue),
                extension = persons.extension(who),
                incall = i%4 == 0,
                disconnected = i%4 == 1,
                ringing = i%4 == 2,
                available = i%4 == 3,
            )
            for i, who in enumerate(self._agents(queue), minute)
        ]

    def pause(self, queue, who):
        """Temporary removes the agent from the queue"""
        self._paused(queue).add(who)

    def resume(self, queue, who):
        """Puts back the agent to the queue"""
        if who in self._paused(queue):
            self._paused(queue).remove(who)

    def addExtension(self, extension, fullname):
        """Setup the extension to be used by fullname"""
        self._extensions.append(ns(
            extension=extension,
            fullname=fullname,
        ))

    def removeExtension(self, extension):
        """Deallocates the extension"""
        self._extensions = [
            ext for ext in self._extensions
            if ext.extension != extension
            ]

    def clearExtensions(self):
        """Deallocates all the extensions"""
        self._extensions = list()

    def extensions(self):
        """Returns the setup extensions"""
        return [(
            #persons.byExtension(info.extension),
            info.extension,
            u"{fullname} <{extension}>".format(**info),
            )
            for info in self._extensions
        ]


# vim: ts=4 sw=4 et
