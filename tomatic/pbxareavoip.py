# -*- coding: utf-8 -*-

from __future__ import absolute_import
import datetime
from yamlns import namespace as ns
import requests
import dbconfig
import json
from .schedulestorage import Storage
from .dbasterisk import DbAsterisk
from .scheduling import choosers, Scheduling
from . import persons

class AreaVoip(object):

    def __init__(self):
        self.config = dbconfig.tomatic.areavoip

    def _api(self, request, **kwds):
        print(request,kwds)
        result = requests.get(self.config.baseurl, params=dict(
            reqtype = request,
            tenant = self.config.tenant,
            key = self.config.apikey,
            **kwds))
        print((result.request.url))
        print(result.text)
        if 'action' in kwds and kwds.get('format') != 'json':
            if result.text.strip() != 'OK':
                raise Exception(result.text.strip())
            return True
        if kwds.get('format') == 'json':
            return result.json()
        return result.text.strip()


    def setQueue(self, queue, names):
        self.clear(queue)
        for name in names:
            self.add(queue, name)


    def queue(self, queue):
        response = self._api('INFO', info='agentsconnected',
            queue = queue,
            format='json',
        )

        if not response: return []
        return [
            ns(
                key = persons.byExtension(extension),
                extension = extension,
                name = persons.name(persons.byExtension(extension)),
                paused = status.get('1') == 'paused',
                disconnected = status['2'] is None or status['2'] == 'UNAVAILABLE',
                available = status['2'] == 'NOT_INUSE',
                ringing = status['2'] == 'RINGING',
                incall = status['2'] == 'INUSE',
                ncalls = int(status['0']),
                secondsInCalls = int(status.get('3','0')),
                secondsSinceLastCall = 0, # TODO
                flags = [status['2']] if status['2'] and status['2'] not in (
                    'UNAVAILABLE', 'NOT_INUSE', 'RINGING', 'INUSE',
                    ) else [],
            )
            for extension, status in response.items()
        ]
    
    def pause(self, queue, name, paused=True):
        extension = persons.extension(name)
        if not extension: return
        response = self._api('AGENT',
            action='pause' if paused else 'unpause',
            queue = queue,
            extension = extension,
            reason = 'notimplemented',
        )

    def resume(self, queue, name):
        self.pause(queue, name, False)

    def add(self, queue, name):
        extension = persons.extension(name)
        if not extension: return
        response = self._api('QUEUE', action='add',
            number = queue,
            extension = extension,
        )

    def clear(self, queue):
        response = self._api('QUEUE', action='clean',
            number = queue,
        )

    def addExtension(self, extension, fullname):
        extensions = self._api('MANAGEDB', object='extension', action='list', format='json')
        for id, extensionInfo in extensions.items():
            if extensionInfo['ex_number'] == extension:
                break
        else:
            return
        jsondata = json.dumps(dict(
            ex_name = fullname,
        ))
        self._api('MANAGEDB',
            object='extension',
            action='update',
            objectid=id,
            jsondata=jsondata,
            format='json',
        )

    def removeExtension(self, extension):
        self.addExtension(extension,'')

    def clearExtensions(self):
        extensions = self._api('MANAGEDB', object='extension', action='list', format='json')
        for id, extensionInfo in extensions.items():
            if not extensionInfo.get('ex_name'):
                continue
            self._api('MANAGEDB',
                object='extension',
                action='update',
                objectid=id,
                jsondata='{"ex_name": ""}',
                format='json',
            )

    def extensions(self):
        extensions = self._api('MANAGEDB', object='extension', action='list', format='json')
        return [(
            extensionInfo['ex_number'],
            extensionInfo['ex_name'],
            )
            for id, extensionInfo in extensions.items()
            if extensionInfo['ex_name']
        ]


class PbxAreaVoip(object):

    def __init__(self, path, *dbargs, **dbkwd):
        self.backend = AreaVoip()
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

    def setSchedQueue(self, when):
        sched = self._currentSched(when)
        if sched is None:
            self.clear()
            return
        week, dow, time = choosers(when)
        self.backend.setQueue(
            self.config.queue,
            sched.peekQueue(dow, time),
            )

    def currentQueue(self):
        return self.backend.queue(self.config.queue)

    def pause(self, name):
        self.backend.pause(self.config.queue, name)

    def resume(self, name):
        self.backend.resume(self.config.queue, name)

    def addLine(self, name):
        self.backend.add(self.config.queue, name)

    def clear(self):
        self.backend.clear(self.config.queue)




# vim: ts=4 sw=4 et
