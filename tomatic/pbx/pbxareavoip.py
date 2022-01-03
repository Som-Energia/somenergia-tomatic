# -*- coding: utf-8 -*-

import requests
import json
from yamlns import namespace as ns
from .. import persons

import dbconfig

class AreaVoip(object):

    defaultQueue = dbconfig.tomatic.get('areavoip',{}).get('queue', None)

    def __init__(self):
        self.config = dbconfig.tomatic.areavoip

    def _api(self, request, **kwds):
        print(request,kwds)
        result = requests.get(self.config.baseurl,
            params=dict(
                reqtype = request,
                tenant = self.config.tenant,
                key = self.config.apikey,
                **kwds),
            timeout=2, # seconds
            )
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
            id = queue,
            extension = extension,
            type='NF', # agent type: non-follow
        )

    def clear(self, queue):
        response = self._api('QUEUE', action='clean',
            id = queue,
        )

    def stats(self, queue, date=None):
        date = date or '{:%Y-%m-%d}'.format(datetime.date.today())
        stats = ns(
            self._api('INFO',
                info='queue',
                id=dbconfig.tomatic.areavoip.queue,
                format='json',
            ),
            DATE=date,
        )
        fields = [
            'date',
            'callsreceived',
            'answeredcalls',
            'abandonedcalls',
            'timedoutcalls',
            'talktime',
            'averagetalktime',
            'holdtime',
            'averageholdtime',
            'maxholdtime',
        ]

        return ns([
            (attr.lower(), stats[attr.upper()])
            for attr in fields
        ])

    def _allExtensions(self):
        return self._api('MANAGEDB',
            object='extension',
            action='list',
            format='json',
        ).items()

    def addExtension(self, extension, fullname):
        for id, extensionInfo in self._allExtensions():
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
        for id, extensionInfo in self._allExtensions():
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
        return [(
            extensionInfo['ex_number'],
            extensionInfo['ex_name'],
            )
            for id, extensionInfo in self._allExtensions()
            if extensionInfo['ex_name']
        ]





# vim: ts=4 sw=4 et
