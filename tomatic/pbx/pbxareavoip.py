# -*- coding: utf-8 -*-

import requests
import json
from yamlns import namespace as ns
from .. import persons
import datetime
import os
from consolemsg import step

class AreaVoip(object):

    @staticmethod
    def defaultQueue():
        import dbconfig
        return dbconfig.tomatic.get('areavoip',{}).get('queue', None)

    def __init__(self):
        import dbconfig
        self.config = dbconfig.tomatic.areavoip

    def _api(self, request, **kwds):
        secondsTimeout = int(kwds.pop('secondsTimeout', 2))
        if os.environ.get('TOMATIC_PBX_DEBUG', False):
            step(f"Calling {result.request.url} {kwds}")
        result = requests.get(self.config.baseurl,
            params=dict(
                reqtype = request,
                tenant = self.config.tenant,
                key = self.config.apikey,
                **kwds),
            timeout=secondsTimeout,
            )
        if os.environ.get('TOMATIC_PBX_DEBUG', False):
            step("Response {}:\n{}\nEnd of response".format(
                result.status_code,
                result.text,
            ))
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

    def old_stats(self, queue, date=None):
        """This gives information limited to the queue,
        which missess calls not even entering the queue,
        so it is deprecated in favor of `stats`
        """
        date = date or '{:%Y-%m-%d}'.format(datetime.date.today())
        stats = ns(
            self._api('INFO',
                info='queue',
                id=queue,
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
            (attr, stats[attr.upper()])
            for attr in fields
        ])

    def calls(self, queue, date=None):
        date = date or datetime.date.today()
        return self._api('INFO',
            info='simplecdrs',
            start=f'{date} 00:00:00',
            end=f'{date} 23:59:59',
            format='json',
            secondsTimeout=10,
        )

    def stats(self, queue, date=None):
        date = date or datetime.date.today()
        cdrs = self.calls(queue, date)
        stats = ns(
            earlycalls = 0,
            latecalls = 0,
            testcalls = 0,
            answeredcalls = 0,
            talktime = 0,
            abandonedcalls = 0,
            timedoutcalls = 0,
            holdtime = 0,
        )
        for cdr in (ns(x) for x in cdrs):
            if cdr.sc_direction != 'IN':
                continue

            if cdr.sc_dialednum not in (
                '872202550',
                '872557980',
            ):
                stats.testcalls += 1
                continue

            if cdr.sc_start < f'{date} 09:00:00':
                stats.earlycalls += 1
                continue
            if cdr.sc_start > f'{date} 14:00:00':
                stats.latecalls += 1
                continue
            if cdr.sc_disposition == 'ANSWERED':
                stats.answeredcalls +=1
                stats.talktime += int(cdr.sc_duration)
            elif cdr.sc_disposition in ('NO ANSWER', 'FAILED', 'BUSY','CONGESTION'):
                stats.abandonedcalls +=1
                stats.holdtime += int(cdr.sc_duration)
            else:
                print(cdr.sc_disposition)
                stats.timedoutcalls +=1
                stats.holdtime += int(cdr.sc_duration)

        def duration(seconds):
            seconds=int(round(seconds))
            return f"{seconds//60//60:02}:{seconds//60%60:02}:{seconds%60%60:02}"

        return ns(
            stats,
            date = str(date),
            callsreceived = len(cdrs),
            averagetalktime = duration(
                stats.talktime/(stats.answeredcalls or 1)
            ),
            averageholdtime = duration(
                stats.holdtime/((stats.abandonedcalls+stats.timedoutcalls) or 1)
            ),
            maxholdtime = duration(max(
                int(cdr.sc_duration)
                for cdr in (ns(x) for x in cdrs)
                if cdr.sc_direction == 'IN'
            )),
            talktime = duration(stats.talktime),
            holdtime = duration(stats.holdtime),
        )

    def _allExtensions(self):
        return self._api('MANAGEDB',
            object='extension',
            action='list',
            format='json',
        ).items()

    def addExtension(self, extension, fullname, email=''):
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
