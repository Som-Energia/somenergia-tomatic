# -*- coding: utf-8 -*-

import datetime
from yamlns import namespace as ns
from consolemsg import error, step
import requests
from enum import Enum
from .. import persons

def TODO(*args, **kwds):
    raise NotImplementedError()

class DeviceStatus(int, Enum):
    Unknown = 0 # Valid but channel didn’t know state
    NotInUse = 1 # Device is not used
    InUse = 2 # Device is in use
    Busy = 3 # Device is busy
    Invalid = 4 # Device is invalid
    Unavailable = 5 # Device is unavailable
    Ringing = 6 # Device is ringing
    InUseRinging = 7 # Device is ringing and in use
    OnHold = 8 # Device is on hold

class BackendError(Exception): pass

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
            raise BackendError()
        self.token = response.json()['token']
        self.bearer = dict(
            authorization=f"Bearer {self.token}",
        )

    def _api(self, method, url, json=None, *args, **kwds):
        '''Calls the Irontec API and process the response'''
        self._login()
        fullurl = self.config.baseurl + url
        step(f"Calling {method} {fullurl} {json or ''}")
        response = requests.request(
            method=method.upper(),
            url=fullurl,
            headers=self.bearer,
            json=json,
        )

        import json
        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            data = response.text

        if response.status_code == 200:
            return data

        if response.status_code == 403: # Method not allowed
            raise BackendError(f"Method not allowed for '{url}'")

        if response.status_code == 420:
            print(data)
            return # TODO: Validation error

        if response.status_code == 550:
            print(data)
            return # TODO: Agent does not exists

        print("Error code:", response.status_code)
        print(response.text)

        raise BackendError(response.json())

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
        self._api('post', '/queue/addagent', json=dict(
            agent = extension,
            queue = queue,
            priority = 1,
            id_dialplan_partition = 1,
        ))

    def clear(self, queue):
        '''Clear all persons in the queue'''
        for agent in self.queue(queue):
            self._api('delete', '/queue/removeagent/'+agent.extension+'/'+queue)

    def queue(self, queue):
        '''Return the state and stats of the persons attending the queue'''
        self._login()
        result = self._api('get', '/queue/status/'+queue)
        return [
            ns(
                extension = agent, # str \d+
                key = persons.byExtension(agent), # str (not from api)
                name = persons.name(persons.byExtension(agent)), # str (not from api)
                paused = status.paused, # bool
                disconnected = status.status in (DeviceStatus.Unavailable, DeviceStatus.Invalid, DeviceStatus.Unknown), # bool
                available = status.status == DeviceStatus.NotInUse, # bool
                ringing = status.status in (DeviceStatus.Ringing, DeviceStatus.InUseRinging), # bool
                incall = status.status in (DeviceStatus.InUse, DeviceStatus.Busy, DeviceStatus.InUseRinging), # bool
                ncalls = status.callstaken, # int (not required)
                secondsInCalls = status.incall, # int (not required)
                secondsSinceLastCall = status.lastcall, # int (not required)
                flags = [
                    ] + ( ['busy'] if status.status == DeviceStatus.Busy else []) + [
                    ] + ( ['inuseringing'] if status.status == DeviceStatus.InUseRinging else []) + [
                    ] + ( ['onhold'] if status.status == DeviceStatus.OnHold else []) + [
                ] # list (any other status not represented by the bools) (not required)
            )
            for agent, status in (
                (x['agent'], ns(x['status']))
                for x in result
            )
        ]
    
    def pause(self, queue, name, paused=True, reason=None):
        '''Pauses (or resumes) the person in the queue'''
        if not paused:
            self.resume(queue, name)
        extension = persons.extension(name)
        if not extension: return
        result = self._api('put', '/agent/pause/'+extension+'/'+queue)

    def resume(self, queue, name):
        """Resumes the person in the queue"""
        extension = persons.extension(name)
        if not extension: return
        result = self._api('put', '/agent/unpause/'+extension+'/'+queue)

    def stats(self, queue, date=None):
        from elasticsearch import Elasticsearch as Searcher
        import dbconfig
        searcher = Searcher(**dbconfig.tomatic.irontec_elk)
        date = date or datetime.date.today()
        starttime = datetime.time(9) # TODO: from config
        stoptime = datetime.time(14) # TODO: from config
 
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
        query = f"""
          bool:
            filter:
              range:
                '@calldate':
                  gte: "{date}T{starttime}"
                  lte: "{date}T{stoptime}"
                  time_zone: "Europe/Madrid"
                  format: strict_date_optional_time
            must:
              match:
                queuename: {dbconfig.tomatic.irontec.queue}
            must_not:
              match:
                # Las the RINGNOANSWER son duplicadas para dejar constancia
                # que se ha intentado llamar a una agente
                hangupcause: RINGNOANSWER
        """
        results = searcher.search(
            index = "sharedstats",
            query = ns.loads(query),
            filter_path=['hits.hits._*'],
        )
        calls = [
            ns(call['_source'])
            for call in results.get("hits",{}).get("hits",[])
        ]

        callsreceived = len(set(call.uniqueid for call in calls))
        answeredcalls = len(set(
            call.uniqueid
            for call in calls
            if call.hangupcause == "ATENDIDA"
        ))
        abandonedcalls = len(set(
            call.uniqueid
            for call in calls
            if call.hangupcause == "PERDIDA"
        ))
        timedoutcalls = len(set(
            call.uniqueid
            for call in calls
            if call.hangupcause == "COLA_TIMEOUT"
        ))
        talktime = sum(
            int(call.agent_time)
            for call in calls
            if call.hangupcause == "ATENDIDA"
        )
        averagetalktime = int(round(talktime/answeredcalls)) if answeredcalls else 0
        holdtime = sum(
            int(call.wait_time)
            for call in calls
            if call.hangupcause != "RINGNOANSWER"
        )
        averageholdtime = int(round(holdtime/callsreceived)) if callsreceived else 0
        maxholdtime = max((
            int(call.get('wait_time',0))
            for call in calls
            if call.hangupcause != "RINGNOANSWER"
        ), default=0)

        return ns(
            date = str(date),
            callsreceived = callsreceived,
            answeredcalls = answeredcalls,
            abandonedcalls = abandonedcalls,
            timedoutcalls = timedoutcalls,
            talktime = talktime,
            averagetalktime = averagetalktime,
            holdtime = holdtime,
            averageholdtime = averageholdtime,
            maxholdtime = maxholdtime,
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
                'àèìòùáéíóúâêîôûäëïöü.ñç,',
                'aeiouaeiouaeiouaeiou nc ',
            ):
                x = x.replace(a,b)
            return x

        self._login()
        if not fullname.startswith('Libre'):
            id = persons.byExtension(extension)
            email = persons.persons().emails.get(id,None)

        try:
            response = self._api(
                'put',
                '/agent/modify', json=dict(
                    agent = extension,
                    name = transliterate(fullname),
                    email = email or 'none@nowhere.com',
                ),
            )
        except BackendError as e:
            error(f"Error loading {extension}, {fullname}, {email}: {e}")

    def removeExtension(self, extension):
        # nameless agents are considered 'deleted'
        self.addExtension(extension, 'Libre')

    def clearExtensions(self):
        minextension = self.config.get('minextension', 100)
        maxextension = self.config.get('maxextension', 399)
        for extension, name, email in self.extensions():
            if int(extension)<=minextension:
                continue
            if int(extension)>maxextension:
                continue
            self.removeExtension(extension)

    def extensions(self):
        self._login()
        json = self._api('get', '/agent/list')
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
