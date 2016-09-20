# -*- coding: utf-8 -*-
from flask import Flask
from htmlgen import HtmlGenFromYaml
import b2btest
import unittest
import scheduleserver
import sys

class scheduleServerTest(unittest.TestCase):
    def setUp(self):
        self.app = scheduleserver.app.test_client()
        self.maxDiff = None
    def test_index_one_tel(self):
        scheduleserver.loadYaml("""\
                setmana: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                hores:
                - 09:00
                - '10:15'
                torns:
                - T1
                colors:
                  ana: 98bdc0
                extensions:
                  ana: 3181
                noms: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                companys:
                - ana
                """
        )
        self.b2bdatapath = "testcases"
        rv = self.app.get('/getqueue/2016_07_25/9/15')
        self.assertB2BEqual(rv.data)

    def test_index_two_tels_intermediate_day(self):
        scheduleserver.loadYaml("""\
                setmana: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                    - tania
                  dm:
                    1:
                    - tania
                    - ana
                    2:
                    - victor
                    - cesar
                    3:
                    - silvia
                    - monica

                hores:
                - 09:00
                - '10:15'
                - '11:30'
                torns:
                - T1
                - T2
                colors:
                  ana:    '98bdc0'
                  tania:  'c8abf4'
                  monica: '7fada0'
                  victor: 'ff3333'
                extensions:
                  ana:   3181
                  tania: 3048
                noms: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                companys:
                - ana
                - monica
                - tania
                - victor
                """
        )
        self.b2bdatapath = "testcases"
        rv = self.app.get('/getqueue/2016_07_26/9/15')
        self.assertB2BEqual(rv.data)

if __name__ == "__main__":

    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True
    
    unittest.main()
# vim: ts=4 sw=4 et
