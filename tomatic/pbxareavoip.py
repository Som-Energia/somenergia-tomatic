# -*- coding: utf-8 -*-

from __future__ import absolute_import
import datetime
from yamlns import namespace as ns
import requests
import dbconfig

from .schedulestorage import Storage
from .dbasterisk import DbAsterisk
from .scheduling import choosers, Scheduling
from . import persons


class PbxAreaVoip(object):

    def __init__(self, path, *dbargs, **dbkwd):
        self.config = dbconfig.tomatic.areavoip
        self.storage = Storage(path)

    def _currentSched(self, when=None):
        when = when or datetime.datetime.now()
        week, dow, time = choosers(when)
        try:
            yaml=self.storage.load(week)
        except KeyError:
            return None
        return Scheduling(yaml)

    def _api(self, request, **kwds):
        print(request,kwds)
        result = requests.get(self.config.baseurl, params=dict(
            reqtype = request,
            tenant = self.config.tenant,
            key = self.config.apikey,
            **kwds))
        print(result.text)
        if 'action' in kwds:
            if result.text.strip() != 'OK':
                raise Exception(result.text)
            return True
        return result.json()

    def setSchedQueue(self, when):
        sched = self._currentSched(when)
        self.clean()
        if sched is None:
            return
        week, dow, time = choosers(when)
        for name in sched.peekQueue(dow, time):
            self.addLine(name)

    def currentQueue(self):
        response = self._api('INFO', info='agentsconnected',
            queue = self.config.queue,
            format='json',
        )

        if not response: return []
        return [
            ns(
                key = persons.byExtension(extension),
                extension = extension,
                name = persons.name(persons.byExtension(extension)),
                paused = status.get('1') == 'paused',
                disconnected = status['2'] == 'UNAVAILABLE',
                available = status['2'] == 'NOT_INUSE',
                ringing = status['2'] == 'RINGING',
                incall = status['2'] == 'INUSE',
                ncalls = int(status['0']),
                secondsInCalls = int(status.get('3','0')),
                secondsSinceLastCall = 0, # TODO
                flags = [status['2']] if status['2'] not in (
                    'UNAVAILABLE', 'NOT_INUSE', 'RINGING', 'INUSE',
                    ) else [],
            )
            for extension, status in response.items()
        ]
    
    def pause(self, name):
        response = self._api('AGENT', action='pause',
            queue = self.config.queue,
            extension = persons.persons().extensions[name],
            reason = 'notimplemented',
        )

    def resume(self, name):
        response = self._api('AGENT', action='unpause',
            queue = self.config.queue,
            extension = persons.persons().extensions[name],
        )

    def addLine(self, name):
        response = self._api('QUEUE', action='add',
            number = self.config.queue,
            extension = persons.persons().extensions[name],
        )

    def clear(self):
        response = self._api('QUEUE', action='clean',
            number = self.config.queue,
        )


# vim: ts=4 sw=4 et
