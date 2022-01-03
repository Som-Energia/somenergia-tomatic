# -*- coding: utf-8 -*-

import datetime
from yamlns import namespace as ns
import requests
import dbconfig
from .. import persons

def TODO(*args, **kwds):
    raise NotImplementedError()

class Irontec(object):

    defaultQueue = dbconfig.tomatic.get('irontec',{}).get('queue',None)

    def __init__(self):
        self.config = dbconfig.tomatic.get('irontec', ns())

    def _api(self, *args, **kwds):
        '''Calls the Irontec API and process the response'''
        TODO()

    # Queue management

    def setQueue(self, queue, names):
        '''Sets fill the queue with the named persons'''
        self.clear(queue)
        for name in names:
            self.add(queue, name)

    def add(self, queue, name):
        '''Add a person to the queue'''
        extension = persons.extension(name)
        if not extension: return
        self._api(...)

    def clear(self, queue):
        '''Clear all persons in the queue'''
        self._api(...)

    def queue(self, queue):
        '''Return the state and stats of the persons attending the queue'''
        response = self._api(...)
        return [
            ns(
                extension = item.extension, # str \d+
                key = persons.byExtension(item.extension), # str (not from api)
                name = persons.name(persons.byExtension(item.extension)), # str (not from api)
                paused = TODO(item), # bool
                disconnected = TODO(item), # bool
                available = TODO(item), # bool
                ringing = TODO(item), # bool
                incall = TODO(item), # bool
                ncalls = TODO(item), # int (not required)
                secondsInCalls = TODO(item), # int (not required)
                secondsSinceLastCall = TODO(item), # int (not required)
                flags = TODO(item) or [], # list (any other status not represented by the bools) (not required)
            )
            for items in TODO(response)
        ]
    
    def pause(self, queue, name, paused=True, reason=None):
        '''Pauses (or resumes) the person in the queue'''
        extension = persons.extension(name)
        if not extension: return
        self._api(...)

    def resume(self, queue, name):
        """Resumes the person in the queue"""
        self.pause(queue, name, False)

    def stats(self, queue, date=None):
        response = self._api(...)
        return ns(
            date = date or '{:%Y-%m-%d}'.format(datetime.date.today()),
            callsreceived = TODO(response),
            answeredcalls = TODO(response),
            abandonedcalls = TODO(response),
            timedoutcalls = TODO(response),
            talktime = TODO(response),
            averagetalktime = TODO(response),
            holdtime = TODO(response),
            averageholdtime = TODO(response),
            maxholdtime = TODO(response),
        )


    # Extension management

    def loadExtensions(self):
        self.clearExtensions()
        for name, extension in persons().extensions.items():
            self.addExtension(
                extension = extension,
                name = name,
                email = persons().emails[name],
            )

    def addExtension(self, extension, fullname, email=''):
        self._api(...)

    def removeExtension(self, extension):
        # nameless agents are considered 'deleted'
        self.addExtension(extension, '', '')

    def clearExtensions(self):
        for item in self.extensions():
            self.removeExtension(item.extension)

    def extensions(self):
        return [
            ns(
                extension = extension(agent),
                name = name(agent),
                email = email(agent),
            )
            for agent in self._api(...)
            # nameless agents are considered 'deleted'
            if name(agent)
        ]

# vim: ts=4 sw=4 et
