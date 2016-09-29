# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from yamlns import namespace as ns


class PbxMockup(object):
    """ """
    def currentQueue(self):
        """ """
        return self._queue

    def reconfigure(self, configuration):
        """ """
        self._queue = [
            ns( key='cesar', paused=False),
        ]

    def __init__(self):
        self._queue = []

class PbxMockup_Test(unittest.TestCase):
    
    def setUp(self):
        weekdays = "dl dm dx dj dv".split()
        now = datetime.now()
        self.today = weekdays[now.weekday()]

    def test_currentQueue_noConfiguration(self):
        pbx = PbxMockup()
        self.assertEqual(pbx.currentQueue(),
            [])

    def test_currentQueue_oneSlot(self):
        pbx = PbxMockup()
        pbx.reconfigure(ns.loads("""\
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


 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
