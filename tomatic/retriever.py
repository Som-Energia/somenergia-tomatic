#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import requests
from consolemsg import step, out

# Dirty Hack: Behave like python3 open regarding unicode
def open(*args, **kwd):
    import codecs
    return codecs.open(encoding='utf8', *args, **kwd)


class Notoi(object):
    'Abstracts Notoi API'
    login_ep = '/login/'
    token_head='JWT '

    def __init__(self, service_url, user, password):
        self.service_url = service_url
        self.token = self.login(user, password)

    def _url(self, ep):
        return self.service_url + ep

    def login(self, username, password):
        login = requests.post(
            self._url(Notoi.login_ep),
            data=dict(
                username = username,
                password = password,
            ),
            verify=False,
        )
        return login.json()['token']

    def absences(self, firstDate, lastDate):
        return self._pagedGet('/absencies/absences',
            start_period = firstDate,
            end_period = lastDate,
        )

    def persons(self):
        return self._pagedGet('/absencies/workers')

    def _pagedGet(self, endpoint, **params):
        url = self._url(endpoint)
        result = []
        while url:
            response = requests.get(
                url,
                params=params,
                headers={
                    'Authorization': Notoi.token_head + self.token,
                },
                verify=False
            )
            params = None
            url = response.json()['next']
            result.extend(response.json()['results'])
        return result


def baixaVacancesNotoi(config):
    step("Baixant vacances del gestor d'absencies...")

    import dbconfig
    notoiApi = Notoi(**dbconfig.tomatic.notoi_data)

    firstDay = addDays(config.monday, -1)
    lastDay = addDays(config.monday, +5)
    absences = notoiApi.absences(firstDay, lastDay)
    notoipersons = [ns(p) for p in notoiApi.persons()]
    email2tomatic = {
        email: id
        for id, email in config.emails.items()
    }
    notoi2tomatic = {
        p.id: email2tomatic[p.email]
        for p in notoipersons
    }

    step("  Guardant indisponibilitats per vacances a 'indisponibilitats-vacances.conf'...")
    translate_days = ['dl', 'dm', 'dx', 'dj', 'dv']

    def dateFromIso(isoString):
        return datetime.datetime.strptime(
                isoString,
                '%Y-%m-%dT%H:%M:%S'
            ).date()

    with open('indisponibilitats-vacances.conf', 'w') as holidaysfile:
        for absence in absences:
            name = notoi2tomatic.get(absence['worker'])
            start = dateFromIso(absence['start_time'])
            end = dateFromIso(absence['end_time'])
            days = [
                translate_days[weekday]
                for weekday in range(5)
                if start <= addDays(config.monday, weekday) <= end
            ]
            for day in days:
                out("+{} {} # vacances", name, day)
                holidaysfile.write("+{} {} # vacances\n".format(name, day))





# vim: et ts=4 sw=4
