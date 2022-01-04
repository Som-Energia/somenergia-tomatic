# -*- coding: utf-8 -*-

import datetime
from yamlns import namespace as ns
from consolemsg import error
import requests
from .. import persons

def TODO(*args, **kwds):
    raise NotImplementedError()

class Irontec(object):

    @staticmethod
    def defaultQueue():
        import dbconfig
        return dbconfig.tomatic.get('irontec',{}).get('queue',None)

    def __init__(self):
        import dbconfig
        self.config = dbconfig.tomatic.get('irontec', ns())
        self.token = None

    def _login(self):
        response = requests.post(
            self.config.baseurl + '/login',
            json = dict(
                username = self.config.user,
                password = self.config.password,
        ))
        if response.status_code != 200:
            raise Exception()
        self.token = response.json()['token']
        self.bearer = dict(
                authorization=f"Bearer {self.token}",
            )

    def _api(self, *args, **kwds):
        '''Calls the Irontec API and process the response'''

        print(response.json())
        return []

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

        def transliterate(x):
            for a,b in zip(
                'àèìòùáéíóúâêîôûäëïöü.',
                'aeiouaeiouaeiouaeiou ',
            ):
                x = x.replace(a,b)
            return x

        self._login()
        if not fullname.startswith('Libre'):
            id = persons.byExtension(extension)
            email = persons.persons().emails.get(id,None)
        response = requests.put(
            self.config.baseurl + '/agent/modify',
            headers=self.bearer,
            json=dict(
                agent = extension,
                name = transliterate(fullname),
                email = email or 'none@nowhere.com',
            ),
        )
        if response.status_code == 200:
            return # Ok

        error(f"Error loading {extension}, {fullname}, {email}")
        if response.status_code == 420:
            print(response.json())
            return # TODO: Validation error

        if response.status_code == 550:
            print(response.json())
            return # TODO: Agent does not exists

        raise Exception(response.json())


    def removeExtension(self, extension):
        # nameless agents are considered 'deleted'
        self.addExtension(extension, 'Libre')

    def clearExtensions(self):
        for item in self.extensions():
            self.removeExtension(item[0])

    def extensions(self):
        self._login()
        response = requests.get(
            self.config.baseurl + '/agent/list',
            headers=self.bearer,
        )
        if response.status_code != 200:
            raise Exception(response.json())
        json = response.json()
        print(json)
        return [
            (
                agent.agent,
                agent.name,
                agent.email,
            )
            for agent in (
                ns(item) for item in json
            )
            # nameless agents are considered 'deleted'
            if not agent.name.startswith('Libre')
        ]

# vim: ts=4 sw=4 et
