# -*- coding: utf-8 -*-
import unittest
from yamlns import namespace as ns
import b2btest
import sys
from parse import parse
import random
from htmlgen import HtmlGenFromYaml, HtmlGenFromSolution
import datetime


class ScheduleHours_Test(unittest.TestCase):
    def eqOrdDict(self, dict1,dict2, msg=None):
         if dict1 == None or dict2 == None:
             self.failureException(msg)

         if type(dict1) is not ns or type(dict2) is not ns:
             self.failureException(msg)
         
         shared_keys = set(dict2.keys()) & set(dict2.keys())        

         if not ( len(shared_keys) == len(dict1.keys()) and len(shared_keys) == len(dict2.keys())):
             self.failureException(msg)
         dicts_are_equal = True
         for key in dict1.keys():
             if type(dict1[key]) is dict:
                 dicts_are_equal = dicts_are_equal and compare_dictionaries(dict1[key],dict2[key])
             else:
                 dicts_are_equal = dicts_are_equal and (dict1[key] == dict2[key])

         if not dicts_are_equal:
             self.failureException(msg)
    def ns(self,content):
        return ns.loads(content)
    def setUp(self):
        self.addTypeEqualityFunc(ns,self.eqOrdDict)
    def test_yamlSolution_oneholiday(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
                    cesar: César
            """),
            solution={},
            date='2016-07-18'
        )
    def test_yamlSolution_oneslot(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
                    cesar: César
            """),
            solution={('dl',0,0):'Ana'},
            date='2016-07-18',
            companys=['Ana']
        )
        self.assertEqual(
            h.getYaml(), 
            ns(
                {'timetable': ns(
                    {'dl': ns(
                        {1: ['Ana']})
                    }),
                  
                  'hores': [
                    '09:00',
                    '10:15'
                  ],
                  'torns': [
                    'T1'
                  ],
                  'colors': ns(
                    {'ana': '98bdc0'}
                  ),
                  'extensions': ns(
                    {'ana': 3181}
                  ),
                  'noms': ns(
                    {'cesar': u'César'}
                  ),
                  'setmana': datetime.date(
                    2016,7,18),
                  'companys': ['Ana']
                }
            )
        )

    def test_htmlTable_oneslot(self):
        h=HtmlGenFromYaml(self.ns("""\
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
            """)
        )

        self.assertMultiLineEqual(
            h.htmlTable(), 
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=1>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
        
    def test_htmlTable_twoTelephonesOneTurnOneDay(self):
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
            hores:
            - 09:00
            - '10:15'
            torns:
            - T1
            - T2
            colors:
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 3181
              jordi: 3183
            noms: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=2>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th><th>T2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
        
    def test_htmlTable_twoTelephonesTwoTurnsOneDay(self):
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
                2:
                - jordi
                - aleix
            hores:
            - 09:00
            - '10:15'
            - '11:30'
            torns:
            - T1
            - T2
            colors:
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 3181
              jordi: 3183
            noms: # Els que no només cal posar en majúscules
               silvia: Sílvia
               monica: Mònica
               tania: Tània
               cesar: César
               victor: Víctor            
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=2>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th><th>T2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>10:15-11:30</th>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")

    def test_htmlTable_twoTelephonesTwoTurnsTwoDays(self):
        self.maxDiff = None
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
                2:
                - jordi
                - aleix
              dm:
                1:
                - victor
                - marta
                2:
                - ana
                - victor
            hores:
            - 09:00
            - '10:15'
            - '11:30'
            torns:
            - T1
            - T2
            colors:
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 3181
              jordi: 3183
            noms: # Els que no només cal posar en majúscules
               silvia: Sílvia
               monica: Mònica
               tania: Tània
               cesar: César
               victor: Víctor
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=2>dl</th><td></td><th colspan=2>dm</th>"""
            u"""</tr>\n"""
            u"""<tr><td></td><th>T1</th><th>T2</th><td></td><th>T1</th><th>T2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>10:15-11:30</th>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
    
    def test_htmlTable_manyTelephonesmanyTurnsmanyDays(self):
        self.maxDiff = None
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
                - pere
                2:
                - jordi
                - aleix
                - pere
                3:
                - carles
                - joan
                - eduard
                4:
                - yaiza
                - joan
                - eduard
              dm:
                1:
                - victor
                - marta
                - ana
                2:
                - ana
                - victor
                - marta
                3:
                - silvia
                - eduard
                - monica
                4:
                - david
                - silvia
                - marc
              dx:
                1:
                - aleix
                - pere
                - yaiza
                2:
                - pere
                - aleix
                - carles
                3:
                - marc
                - judit
                - victor
                4:
                - david
                - silvia
                - victor
              dj:
                1:
                - judit
                - jordi
                - carles
                2:
                - joan
                - silvia
                - jordi
                3:
                - monica
                - marc
                - tania
                4:
                - tania
                - monica
                - marc
              dv:
                1:
                - marta
                - victor
                - judit
                2:
                - victor
                - joan
                - judit
                3:
                - eduard
                - yaiza
                - jordi
                4:
                - jordi
                - carles
                - aleix
            hores:
            - 09:00
            - '10:15'
            - '11:30'
            - '12:45'
            - '14:00'
            torns:
            - T1
            - T2
            - T3
            noms: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=3>dl</th>"""
            u"""<td></td><th colspan=3>dm</th>"""
            u"""<td></td><th colspan=3>dx</th>"""
            u"""<td></td><th colspan=3>dj</th>"""
            u"""<td></td><th colspan=3>dv</th></tr>\n"""
            u"""<tr>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td class='yaiza'>Yaiza</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>10:15-11:30</th>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>11:30-12:45</th>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td class='monica'>Mònica</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='monica'>Mònica</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td class='tania'>Tània</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td class='yaiza'>Yaiza</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>12:45-14:00</th>\n"""
            u"""<td class='yaiza'>Yaiza</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='david'>David</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='david'>David</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='tania'>Tània</td>\n"""
            u"""<td class='monica'>Mònica</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
    def test_htmlExtension_oneExtension(self):
        h = HtmlGenFromYaml(self.ns("""\
            extensions:
               marta:  3040
            noms:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")
    
    def test_htmlExtension_twoExtensions(self):
        h = HtmlGenFromYaml(self.ns("""\
            extensions:
               marta:  3040
               aleix:  3053
            noms:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """<div class="extension aleix">Aleix<br/>3053</div>\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")

    def test_htmlExtension_noExtensions(self):
        h = HtmlGenFromYaml(self.ns("""\
            noms:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """</div>""")

    def test_htmlHeader_properSetmana(self):
        h = HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
                """)
        )
        self.assertMultiLineEqual(h.htmlSetmana(),"""<h1>Setmana 2016-07-25</h1>""")

    def test_htmlHeader_noSetmana(self):
        h = HtmlGenFromYaml(self.ns("""\
            noms:
               cesar: César
                """)
        )
        self.assertMultiLineEqual(h.htmlSetmana(),"""<h1>Setmana ???</h1>""")

    def test_htmlColors_oneColor(self):
        h = HtmlGenFromYaml(self.ns("""\
            colors:
               marc: fbe8bc
            companys:
            - marc
                """)
        )
        self.assertMultiLineEqual(
            h.htmlColors(),
            """.marc { background-color: #fbe8bc; }"""
        )

    def test_htmlColors_randomColor(self):
        h = HtmlGenFromYaml(self.ns("""\
            companys:
            - cesar
                """)
        )
        self.assertRegexpMatches(parse(
            """.cesar {{ background-color: {} }}""",
                  h.htmlColors()
                  )[0],
            '#[0-9a-f]{6};'
        )

    def test_htmlParse_completeHtml(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - jordi
            - pere
            2:
            - jordi
            - aleix
            - pere
            3:
            - carles
            - joan
            - eduard
            4:
            - yaiza
            - joan
            - eduard
          dm:
            1:
            - victor
            - marta
            - ana
            2:
            - ana
            - victor
            - marta
            3:
            - silvia
            - eduard
            - monica
            4:
            - david
            - silvia
            - marc
          dx:
            1:
            - aleix
            - pere
            - yaiza
            2:
            - pere
            - aleix
            - carles
            3:
            - marc
            - judit
            - victor
            4:
            - david
            - silvia
            - victor
          dj:
            1:
            - judit
            - jordi
            - carles
            2:
            - joan
            - silvia
            - jordi
            3:
            - monica
            - marc
            - tania
            4:
            - tania
            - monica
            - marc
          dv:
            1:
            - marta
            - victor
            - judit
            2:
            - victor
            - joan
            - judit
            3:
            - eduard
            - yaiza
            - jordi
            4:
            - jordi
            - carles
            - aleix
        hores:
        - 09:00
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        torns:
        - T1
        - T2
        - T3
        colors:
          marc: fbe8bc
          eduard: d8b9c5
          pere: 8f928e
          david: ffd3ac
          aleix: eed0eb
          carles: c98e98
          marta: eb9481
          monica: 7fada0
          yaiza: 90cdb9
          erola: 8789c8
          manel: 88dfe3
          tania: c8abf4
          judit: e781e8
          silvia: 8097fa
          joan: fae080
          ana: 98bdc0
          victor: ff3333
          jordi: ff9999
          judith: cb8a85
        extensions:
          marta: 3040
          monica: 3041
          manel: 3042
          erola: 3043
          yaiza: 3044
          eduard: 3045
          marc: 3046
          judit: 3047
          judith: 3057
          tania: 3048
          carles: 3051
          pere: 3052
          aleix: 3053
          david: 3054
          silvia: 3055
          joan: 3056
          ana: 3181
          victor: 3182
          jordi: 3183
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        companys:
        - marta
        - monica
        - manel
        - erola
        - yaiza
        - eduard
        - marc
        - judit
        - judith
        - tania
        - carles
        - pere
        - aleix
        - david
        - silvia
        - joan
        - ana
        - victor
        - jordi""")
       )
       self.b2bdatapath = "testcases"
       self.assertB2BEqual(h.htmlParse().encode('utf-8'))

if __name__ == "__main__":

    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True
    
    unittest.main()
# vim: ts=4 sw=4 et
