# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from yamlns import namespace as ns


class PbxMockup(object):
    """ """

    def __init__(self):
        self._queue = []

    def reconfigure(self, configuration):
        from bisect import bisect
        now = datetime.now()
        currentHour = "{:%H:%m}".format(now)
        turn = bisect(configuration.hores, currentHour)
        if turn == 0: return []
        self._queue = [
            ns( key=who, paused=False)
            for who in configuration.timetable.dx[turn]
            ]

    def currentQueue(self):
        return self._queue


class PbxMockup_Test(unittest.TestCase):
    ""

    def setUp(self):
        weekdays = "dl dm dx dj dv".split()
        now = datetime.now()
        self.today = weekdays[now.weekday()]
        self.currentHour = now.hour

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





unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
