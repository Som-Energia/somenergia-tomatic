# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timedelta
from yamlns import namespace as ns

def weekday(date):
    weekdays = "dl dm dx dj dv ds dg".split()
    return weekdays[date.weekday()]

class PbxMockup(object):
    """ """

    def __init__(self):
        self._configuration = ns.loads(u"""
            timetable: {}
            hores: []
            """)

    def reconfigure(self, configuration):
        self._configuration = configuration

    def currentQueue(self):
        timetable = self._configuration.timetable
        now = datetime.now()
        from bisect import bisect
        currentHour = "{:%H:%m}".format(now)
        turn = bisect(self._configuration.hores, currentHour)
        wd = weekday(now)
        if wd not in timetable: return []
        if turn not in timetable[wd]: return []
        return [
            ns( key=who, paused=False)
            for who in timetable[wd][turn]
            ]


class PbxMockup_Test(unittest.TestCase):
    ""

    def setUp(self):
        now = datetime.now()
        self.today = weekday(now)
        self.currentHour = now.hour
        self.nextday = weekday(now+timedelta(days=1))

    def test_currentQueue_noConfiguration(self):
        pbx = PbxMockup()
        result = pbx.currentQueue()
        self.assertEqual(result, [])

    def test_currentQueue_oneSlot_oneTurn(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
            - '00:00'
            - '23:59'
            
            extensions:
              cesar: 200
            """.format(
                today=self.today
            )))
        self.assertEqual(pbx.currentQueue(), [
            ns( key='cesar', paused=False),
            ])

    def test_currentQueue_twoSlots(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
                2:
                - eduard
            hores:
            - '00:00'
            - '{splithour}:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                splithour=self.currentHour,
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ns( key='eduard', paused=False),
            ])

    def test_currentQueue_beforeSlots(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
            - '23:58'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_currentQueue_afterSlots(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {today}:
                1:
                - cesar
            hores:
            - '00:00'
            - '00:01'

            extensions:
              cesar: 200
            """.format(
                today=self.today,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])

    def test_currentQueue_afterSlots(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads(u"""\
            timetable:
              {nextday}:
                1:
                - cesar
            hores:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """.format(
                nextday=self.nextday,
            )))
        self.assertEqual(pbx.currentQueue(), [
            ])





unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
