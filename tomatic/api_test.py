# -*- coding: utf-8 -*-

import b2btest
import unittest
from yamlns import namespace as ns
from datetime import datetime

from .htmlgen import HtmlGen
from .asterisk import HtmlGenFromAsterisk
from . import api

config=None
try:
    import config
except ImportError:
    pass

def setNow(year,month,day,hour,minute):
    api.now=datetime(year,month,day,hour,minute)

def loadYaml(yaml):
    parsedYaml = ns.loads(yaml)
    week = str(parsedYaml.week)
    api.hs[week]=HtmlGen(parsedYaml)

startOfWeek = HtmlGen.iniciSetmana(
    datetime.now()
)

def loadAsterisk(yaml,week=None):
    global startOfWeek
    api.hs[startOfWeek.strftime("%Y-%m-%d")
        ]=HtmlGenFromAsterisk(
            yaml,pbx().receiveConf()
        )
@unittest.skip("Not made work again")
class Api_Test(unittest.TestCase):

    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        self.maxDiff = None
        self.b2bdatapath = "testdata"

    def test_getcurrentqueue(self):

        loadYaml("""\
                week: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                hours:
                - '09:00'
                - '10:15'
                turns:
                - T1
                colors:
                   marc:   'fbe8bc'
                   eduard: 'd8b9c5'
                   pere:   '8f928e'
                   david:  'ffd3ac'
                   aleix:  'eed0eb'
                   carles: 'c98e98'
                   marta:  'eb9481'
                   monica: '7fada0'
                   yaiza:  '90cdb9'
                   erola:  '8789c8'
                   manel:  '88dfe3'
                   tania:  'c8abf4'
                   judit:  'e781e8'
                   silvia: '8097fa'
                   joan:   'fae080'
                   ana:    '98bdc0'
                   victor: 'ff3333'
                   jordi: 'ff9999' 
                extensions:
                  ana: 217
                  pere: 218
                  jordi: 219
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        api.setNow(2016, 7, 25, 9, 15)
        rv = self.app.get('/')
        self.assertB2BEqual(rv.data)

    def test_getqueue_one_tel(self):
        loadYaml("""\
                week: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                hours:
                - '09:00'
                - '10:15'
                turns:
                - T1
                colors:
                   marc:   'fbe8bc'
                   eduard: 'd8b9c5'
                   pere:   '8f928e'
                   david:  'ffd3ac'
                   aleix:  'eed0eb'
                   carles: 'c98e98'
                   marta:  'eb9481'
                   monica: '7fada0'
                   yaiza:  '90cdb9'
                   erola:  '8789c8'
                   manel:  '88dfe3'
                   tania:  'c8abf4'
                   judit:  'e781e8'
                   silvia: '8097fa'
                   joan:   'fae080'
                   ana:    '98bdc0'
                   victor: 'ff3333'
                   jordi: 'ff9999' 
                extensions:
                  ana: 217
                  pere: 218
                  jordi: 219
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        rv = self.app.get('/getqueue/2016-07-25/9/15')
        self.assertB2BEqual(rv.data)

    def test_getqueue_many_tt_first_week(self):
        loadYaml("""\
                week: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                hours:
                - '09:00'
                - '10:15'
                turns:
                - T1
                colors:
                   marc:   'fbe8bc'
                   eduard: 'd8b9c5'
                   pere:   '8f928e'
                   david:  'ffd3ac'
                   aleix:  'eed0eb'
                   carles: 'c98e98'
                   marta:  'eb9481'
                   monica: '7fada0'
                   yaiza:  '90cdb9'
                   erola:  '8789c8'
                   manel:  '88dfe3'
                   tania:  'c8abf4'
                   judit:  'e781e8'
                   silvia: '8097fa'
                   joan:   'fae080'
                   ana:    '98bdc0'
                   victor: 'ff3333'
                   jordi: 'ff9999' 
                extensions:
                  ana: 217
                  pere: 218
                  jordi: 219
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        loadYaml("""\
                week: 2016-08-01
                timetable:
                  dl:
                    1:
                    - victor
                hours:
                - '09:00'
                - '10:15'
                turns:
                - T1
                colors:
                  ana:    '98bdc0'
                  tania:  'c8abf4'
                  monica: '7fada0'
                  victor: 'ff3333'
                extensions:
                  ana: 217
                  pere: 218
                  jordi: 219
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        rv = self.app.get('/getqueue/2016-07-25/9/15')
        self.assertB2BEqual(rv.data)

    def test_getqueue_many_tt_second_week(self):
        loadYaml("""\
                week: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                hours:
                - '09:00'
                - '10:15'
                turns:
                - T1
                colors:
                  ana:    '98bdc0'
                  tania:  'c8abf4'
                  monica: '7fada0'
                  victor: 'ff3333'
                extensions:
                  ana: 217
                  pere: 218
                  jordi: 219
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        loadYaml("""\
                week: 2016-08-01
                timetable:
                  dl:
                    1:
                    - victor
                hours:
                - '09:00'
                - '10:15'
                turns:
                - T1
                colors:
                  ana:    '98bdc0'
                  tania:  'c8abf4'
                  monica: '7fada0'
                  victor: 'ff3333'
                extensions:
                  ana: 3181
                  victor: 3182
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        rv = self.app.get('/getqueue/2016-08-01/9/15')
        self.assertB2BEqual(rv.data)

    def test_getqueue_two_tels_intermediate_day(self):
        loadYaml("""\
                week: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                    - tania
                  dm:
                    1:
                    - tania
                    - victor
                    2:
                    - victor
                    - cesar
                    3:
                    - silvia
                    - monica

                hours:
                - '09:00'
                - '10:15'
                - '11:30'
                turns:
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
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                """
        )
        rv = self.app.get('/getqueue/2016-07-26/9/15')
        self.assertB2BEqual(rv.data)

    def test_getDynamicqueue_three_tels_intermediate_day(self):
        loadYaml("""\
                week: 2016-07-25
                timetable:
                  dl:
                    1:
                    - ana
                    - tania
                  dm:
                    1:
                    - tania
                    - victor
                    2:
                    - victor
                    - cesar
                    3:
                    - silvia
                    - monica

                hours:
                - '09:00'
                - '10:15'
                - '11:30'
                turns:
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
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                dynamic:
                - ana
                - monica
                - tania
                """
        )
        rv = self.app.get('/getqueue/2016-07-26/9/15')
        self.assertB2BEqual(rv.data)

    @unittest.skipIf(not config, "depends on pbx")
    def test_receiveFromAsterisk_firstTurn(self):
        yaml = ns.loads("""\
                week: 2016-09-26
                timetable:
                  dl:
                    1:
                    - ana
                    - tania
                  dm:
                    1:
                    - tania
                    - victor
                    2:
                    - victor
                    - cesar
                    3:
                    - silvia
                    - monica

                hours:
                - '09:00'
                - '10:15'
                - '11:30'
                turns:
                - T1
                - T2
                - T3
                colors:
                   marc:   'fbe8bc'
                   eduard: 'd8b9c5'
                   pere:   '8f928e'
                   david:  'ffd3ac'
                   aleix:  'eed0eb'
                   carles: 'c98e98'
                   marta:  'eb9481'
                   monica: '7fada0'
                   yaiza:  '90cdb9'
                   erola:  '8789c8'
                   manel:  '88dfe3'
                   tania:  'c8abf4'
                   judit:  'e781e8'
                   silvia: '8097fa'
                   joan:   'fae080'
                   ana:    '98bdc0'
                   victor: 'ff3333'
                   jordi: 'ff9999' 
                   judith: 'b8aeed'
                   cesar:  'fe9a2e'
                extensions:
                  cesar:  200
                  marta:  206
                  monica: 216
                  manel:  212
                  erola:  213
                  yaiza:  205
                  eduard: 222
                  marc:   203
                  judit:  202
                  judith: 211
                  tania:  208
                  carles: 223
                  pere:   224
                  aleix:  214
                  david:  204
                  silvia: 207
                  joan:   215
                  ana:    217
                  victor: 218
                  jordi:  210
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                dynamic:
                - ana
                - monica
                - tania
                """
        )
        api.loadAsterisk(yaml,
            week=datetime(2016,9,19,9,26))
        rv = self.app.get('/getqueue/'
        '2016-09-26/9/19')
        self.assertB2BEqual(rv.data)

    @unittest.skipIf(not config, "depends on pbx")
    def test_receiveFromAsterisk_secondTurn(self):
        yaml = ns.loads("""\
                week: 2016-09-26
                timetable:
                  dl:
                    1:
                    - ana
                    - tania
                  dm:
                    1:
                    - tania
                    - victor
                    2:
                    - victor
                    - cesar
                    3:
                    - silvia
                    - monica

                hours:
                - '09:00'
                - '10:15'
                - '11:30'
                turns:
                - T1
                - T2
                - T3
                colors:
                   marc:   'fbe8bc'
                   eduard: 'd8b9c5'
                   pere:   '8f928e'
                   david:  'ffd3ac'
                   aleix:  'eed0eb'
                   carles: 'c98e98'
                   marta:  'eb9481'
                   monica: '7fada0'
                   yaiza:  '90cdb9'
                   erola:  '8789c8'
                   manel:  '88dfe3'
                   tania:  'c8abf4'
                   judit:  'e781e8'
                   silvia: '8097fa'
                   joan:   'fae080'
                   ana:    '98bdc0'
                   victor: 'ff3333'
                   jordi: 'ff9999' 
                   judith: 'b8aeed'
                   cesar:  'fe9a2e'
                extensions:
                  cesar:  200
                  marta:  206
                  monica: 216
                  manel:  212
                  erola:  213
                  yaiza:  205
                  eduard: 222
                  marc:   203
                  judit:  202
                  judith: 211
                  tania:  208
                  carles: 223
                  pere:   224
                  aleix:  214
                  david:  204
                  silvia: 207
                  joan:   215
                  ana:    217
                  victor: 218
                  jordi:  210
                names: # Els que no només cal posar en majúscules
                  silvia: Sílvia
                  monica: Mònica
                  tania: Tània
                  cesar: César
                  victor: Víctor
                dynamic:
                - ana
                - monica
                - tania
                """
        )
        api.loadAsterisk(yaml,
            week=datetime(2016,9,19,9,26))
        rv = self.app.get('/getqueue/'
        '2016-09-26/10/20')
        self.assertB2BEqual(rv.data)

if __name__ == "__main__":

    import sys
    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True

    unittest.main()

# vim: ts=4 sw=4 et
