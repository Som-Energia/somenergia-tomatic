#-*- coding: utf-8 -*-

import unittest
from yamlns import namespace as ns
import b2btest
import sys

from .htmlgen import HtmlGen
from .htmlgen import schedule2asterisk

class Schedule_Test(unittest.TestCase):

    def eqOrdDict(self, dict1, dict2, msg=None):
        def sorteddict(d):
            if type(d) not in (dict, ns):
                return d
            return ns(sorted(
                (k, sorteddict(v))
                for k,v in d.items()
                ))
        dict1 = sorteddict(dict1)
        dict2 = sorteddict(dict2)

        return self.assertMultiLineEqual(dict1.dump(), dict2.dump(), msg)

    def ns(self,content):
        return ns.loads(content)

    def setUp(self):
        self.maxDiff = None
        self.b2bdatapath = "testdata"
        self.addTypeEqualityFunc(ns,self.eqOrdDict)

    def test_htmlTable_oneslot(self):
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            colors:
              ana: aa11aa
            extensions:
              ana: 1001
            names: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )

        self.assertMultiLineEqual(
            h.htmlTable(),
            u"<table>\n"
            u"<tr><td></td><th colspan=1>dl</th></tr>\n"
            u"<tr><td></td><th>L1</th>"
            u"</tr>\n"""
            u"<tr><th>09:00-10:15</th>\n"
            u"<td class='ana'>Ana</td>\n"
            u"</tr>\n"
            u"</table>")

    def test_htmlTable_twoTelephonesOneTurnOneDay(self):
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
                - jordi
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            - L2
            colors:
              ana: aa11aa
              jordi: ff9999
            extensions:
              ana: 1001
              jordi: 3183
            names: # Els que no només cal posar en majúscules
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
            u"""<tr><td></td><th>L1</th><th>L2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")

    def test_htmlTable_twoTelephonesTwoTurnsOneDay(self):
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
                - jordi
              - - jordi
                - aleix
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            turns:
            - L1
            - L2
            colors:
              ana: aa11aa
              jordi: ff9999
            extensions:
              ana: 1001
              jordi: 3183
            names: # Els que no només cal posar en majúscules
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
            u"""<tr><td></td><th>L1</th><th>L2</th>"""
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
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              -
                - ana
                - jordi
              -
                - jordi
                - aleix
              dm:
              -
                - victor
                - marta
              -
                - ana
                - victor
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            turns:
            - L1
            - L2
            colors:
              ana: aa11aa
              jordi: ff9999
            extensions:
              ana: 1001
              jordi: 3183
            names: # Els que no només cal posar en majúscules
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
            u"""<tr><td></td><th>L1</th><th>L2</th><td></td><th>L1</th><th>L2</th>"""
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
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              -
                - ana
                - jordi
                - pere
              -
                - jordi
                - aleix
                - pere
              -
                - carles
                - joan
                - eduard
              -
                - yaiza
                - joan
                - eduard
              dm:
              -
                - victor
                - marta
                - ana
              -
                - ana
                - victor
                - marta
              -
                - silvia
                - eduard
                - monica
              -
                - david
                - silvia
                - marc
              dx:
              -
                - aleix
                - pere
                - yaiza
              -
                - pere
                - aleix
                - carles
              -
                - marc
                - judit
                - victor
              -
                - david
                - silvia
                - victor
              dj:
              -
                - judit
                - jordi
                - carles
              -
                - joan
                - silvia
                - jordi
              -
                - monica
                - marc
                - tania
              -
                - tania
                - monica
                - marc
              dv:
              -
                - marta
                - victor
                - judit
              -
                - victor
                - joan
                - judit
              -
                - eduard
                - yaiza
                - jordi
              -
                - jordi
                - carles
                - aleix
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            - '12:45'
            - '14:00'
            turns:
            - L1
            - L2
            - L3
            names: # Els que no només cal posar en majúscules
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
            u"""<td></td><th>L1</th><th>L2</th><th>L3</th>"""
            u"""<td></td><th>L1</th><th>L2</th><th>L3</th>"""
            u"""<td></td><th>L1</th><th>L2</th><th>L3</th>"""
            u"""<td></td><th>L1</th><th>L2</th><th>L3</th>"""
            u"""<td></td><th>L1</th><th>L2</th><th>L3</th>"""
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
        h = HtmlGen(self.ns("""\
            extensions:
               marta:  3040
            names:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n"""
        """<div class="extensions">\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")

    def test_htmlExtension_twoExtensions(self):
        h = HtmlGen(self.ns("""\
            extensions:
               marta:  3040
               aleix:  3053
            names:
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
        h = HtmlGen(self.ns("""\
            names:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n"""
        """<div class="extensions">\n"""
        """</div>""")

    def test_htmlHeader_properSetmana(self):
        h = HtmlGen(self.ns("""\
            week: '2016-07-25'
                """)
        )
        self.assertMultiLineEqual(h.htmlSetmana(),"""<h1>Setmana 2016-07-25</h1>""")

    def test_htmlHeader_noSetmana(self):
        h = HtmlGen(self.ns("""\
            names:
               cesar: César
                """)
        )
        self.assertMultiLineEqual(h.htmlSetmana(),"""<h1>Setmana ???</h1>""")

    def test_htmlColors_oneColor(self):
        h = HtmlGen(self.ns("""\
            colors:
               marc: fbe8bc
            extensions:
              marc: 666
                """)
        )
        self.assertMultiLineEqual(
            h.htmlColors(),
            """.marc     { background-color: #fbe8bc; }"""
        )

    def test_htmlColors_forceRandomColor(self):
        h = HtmlGen(self.ns("""\
            colors:
               marc: fbe8bc
            randomColors: true
            extensions:
              cesar: 555
                """)
        )
        colors = h.htmlColors()
        self.assertNotEqual(
            colors,
            """.marc      { background-color: #fbe8bc; }"""
        )

        self.assertRegex(
            colors,
            r"\.marc    * \{ background-color: #[0-9a-f]{6}; }",
        )

    def test_htmlColors_randomColor(self):
        h = HtmlGen(self.ns("""\
            extensions:
              cesar: 555
                """)
        )
        self.assertRegex(
            h.htmlColors(),
            r"\.cesar    *\{ background-color: #[0-9a-f]{6}; \}",
            )

    def test_html_completeHtml(self):
       h = HtmlGen(self.ns("""\
        timetable:
          dl:
          -
            - ana
            - jordi
            - pere
          -
            - jordi
            - aleix
            - pere
          -
            - carles
            - joan
            - eduard
          -
            - yaiza
            - joan
            - eduard
          dm:
          -
            - victor
            - marta
            - ana
          -
            - ana
            - victor
            - marta
          -
            - silvia
            - eduard
            - monica
          -
            - david
            - silvia
            - marc
          dx:
          -
            - aleix
            - pere
            - yaiza
          -
            - pere
            - aleix
            - carles
          -
            - marc
            - judit
            - victor
          -
            - david
            - silvia
            - victor
          dj:
          -
            - judit
            - jordi
            - carles
          -
            - joan
            - silvia
            - jordi
          -
            - monica
            - marc
            - tania
          -
            - tania
            - monica
            - marc
          dv:
          -
            - marta
            - victor
            - judit
          -
            - victor
            - joan
            - judit
          -
            - eduard
            - yaiza
            - jordi
          -
            - jordi
            - carles
            - aleix
        hours:
        - '09:00'
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        turns:
        - L1
        - L2
        - L3
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
          ana: aa11aa
          victor: ff3333
          jordi: ff9999
          judith: cb8a85
          cesar:  '889988'
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
          ana: 1001
          victor: 3182
          jordi: 3183
        week: '2016-07-25'
        names: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        """)
       )
       self.assertB2BEqual(h.html().encode('utf-8'))

    def test_html_completeHtmlWithHoliday(self):
       h = HtmlGen(self.ns("""\
        timetable:
          dl:
          -
            - festiu
            - festiu
            - festiu
          -
            - festiu
            - festiu
            - festiu
          -
            - festiu
            - festiu
            - festiu
          -
            - festiu
            - festiu
            - festiu
          dm:
          -
            - victor
            - marta
            - ana
          -
            - ana
            - victor
            - marta
          -
            - silvia
            - eduard
            - monica
          -
            - david
            - silvia
            - marc
          dx:
          -
            - aleix
            - pere
            - yaiza
          -
            - pere
            - aleix
            - carles
          -
            - marc
            - judit
            - victor
          -
            - david
            - silvia
            - victor
          dj:
          -
            - judit
            - jordi
            - carles
          -
            - joan
            - silvia
            - jordi
          -
            - monica
            - marc
            - tania
          -
            - tania
            - monica
            - marc
          dv:
          -
            - marta
            - victor
            - judit
          -
            - victor
            - joan
            - judit
          -
            - eduard
            - yaiza
            - jordi
          -
            - jordi
            - carles
            - aleix
        hours:
        - '09:00'
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        turns:
        - L1
        - L2
        - L3
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
          ana: aa11aa
          victor: ff3333
          jordi: ff9999
          judith: cb8a85
          cesar:  '889988'
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
          ana: 1001
          victor: 3182
          jordi: 3183
        week: '2016-07-25'
        names: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        """)
       )
       self.assertB2BEqual(h.html().encode('utf-8'))

    def test_nameToExtension_oneSip(self):
        yaml = """\
            timetable:
              dl:
              -
                - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            names: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            colors:
              ana: aa11aa
            extensions:
              ana: 217
            week: '2016-07-25'
            """
        h = HtmlGen(self.ns(yaml))
        self.assertEqual(h.nameToExtension('ana'),217)

    def test_nameToExtension_manySip(self):
        yaml = """\
        timetable:
          dl:
          -
            - ana
            - pere
            - jordi
        hours:
        - '09:00'
        - '10:15'
        turns:
        - L1
        - L2
        - L3
        colors:
          pere: 8f928e
          ana: aa11aa
          jordi: ff9999
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
        week: '2016-07-25'
        """
        h = HtmlGen(self.ns(yaml))
        self.assertEqual(h.nameToExtension('ana'),217)

    def test_extensionToName_oneSip(self):
        yaml = """\
        timetable:
          dl:
          -
            - ana
            - pere
            - jordi
        hours:
        - '09:00'
        - '10:15'
        turns:
        - L1
        - L2
        - L3
        names: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        colors:
          pere: 8f928e
          ana: aa11aa
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """
        h = HtmlGen(self.ns(yaml))
        self.assertEqual(h.extensionToName(217),'ana')

    def test_extensionToName_manySip(self):
        yaml = """\
        timetable:
          dl:
          -
            - ana
            - pere
            - jordi
        hours:
        - '09:00'
        - '10:15'
        turns:
        - L1
        - L2
        - L3
        colors:
          pere: 8f928e
          ana: aa11aa
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """
        h = HtmlGen(self.ns(yaml))
        self.assertEqual(h.extensionToName(217),'ana')

    def test_partialCoreTable_getFirstTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi

        hours:
        - '09:00'
        - '10:15'

        names: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor

        turns:
        - L1
        - L2
        - L3
        colors:
          pere: 8f928e
          ana: aa11aa
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """
        h = HtmlGen(self.ns(yaml))
        self.assertEqual(h.partialCoreTable('dl',1), (
             u"""<td class='ana'>Ana</td>\n"""
             u"""<td class='pere'>Pere</td>\n"""
             u"""<td class='jordi'>Jordi</td>\n"""
             )
        )
    def test_partialCoreTable_getSecondTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
            2:
            - jordi
            - pere
            - ana
        hours:
        - '09:00'
        - '10:15'
        - '11:30'

        names: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor

        turns:
        - L1
        - L2
        - L3
        colors:
          pere: 8f928e
          ana: aa11aa
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        week: '2016-07-25'
        """
        h = HtmlGen(self.ns(yaml))
        self.assertEqual(h.partialCoreTable('dl',2), (
             u"""<td class='jordi'>Jordi</td>\n"""
             u"""<td class='pere'>Pere</td>\n"""
             u"""<td class='ana'>Ana</td>\n"""
             )
        )

    def test_schedule2asterisk_oneTurnOneLocal(self):
        configuration = schedule2asterisk(self.ns("""\
            timetable:
              dl:
              -
                - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            colors:
              pere: 8f928e
              ana: aa11aa
              jordi: ff9999
            extensions:
              ana: 217
            week: '2016-07-25'
            names: # Els que no només cal posar en majúscules
               silvia: Sílvia
               monica: Mònica
               tania: Tània
               cesar: César
               victor: Víctor
            """))
        self.assertMultiLineEqual(configuration,
            u"""[entrada_cua_dl_1]\n"""
            u"""music=default\n"""
            u"""strategy=linear\n"""
            u"""eventwhencalled=yes\n"""
            u"""timeout=15\n"""
            u"""retry=1\n"""
            u"""wrapuptime=0\n"""
            u"""maxlen = 0\n"""
            u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
            u"""Periodic-announce-frequency = 15\n"""
            u"""announce-frequency = 0\n"""
            u"""announce-holdtime = no\n"""
            u"""announce-position =no\n"""
            u"""context = bustia_veu\n"""
            u"""member = SIP/217,1\n"""
           )

    def test_schedule2asterisk_manyTurnOneLocal(self):
        configuration = schedule2asterisk(self.ns("""\
            timetable:
              dl:
              -
                - ana
                - jordi
                - pere
              -
                - jordi
                - aleix
                - pere
              -
                - carles
                - joan
                - eduard
              -
                - yaiza
                - joan
                - eduard
              dm:
              -
                - victor
                - marta
                - ana
              -
                - ana
                - victor
                - marta
              -
                - silvia
                - eduard
                - monica
              -
                - david
                - silvia
                - marc
              dx:
              -
                - aleix
                - pere
                - yaiza
              -
                - pere
                - aleix
                - carles
              -
                - marc
                - judit
                - victor
              -
                - david
                - silvia
                - victor
              dj:
              -
                - judit
                - jordi
                - carles
              -
                - joan
                - silvia
                - jordi
              -
                - monica
                - marc
                - tania
              -
                - tania
                - monica
                - marc
              dv:
              -
                - marta
                - victor
                - judit
              -
                - victor
                - joan
                - judit
              -
                - eduard
                - yaiza
                - jordi
              -
                - jordi
                - carles
                - aleix
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            - '12:45'
            - '14:00'
            turns:
            - L1
            - L2
            - L3
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
              ana: aa11aa
              victor: ff3333
              jordi: ff9999
              judith: cb8a85
            extensions:
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
            week: '2016-07-25'
            names: # Els que no només cal posar en majúscules
               silvia: Sílvia
               monica: Mònica
               tania: Tània
               cesar: César
               victor: Víctor
            """)
        )
        self.assertMultiLineEqual(configuration,
        u"""[entrada_cua_dl_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/217,1\n"""
        u"""member = SIP/210,2\n"""
        u"""member = SIP/224,3\n"""
        u"""[entrada_cua_dl_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/210,1\n"""
        u"""member = SIP/214,2\n"""
        u"""member = SIP/224,3\n"""
        u"""[entrada_cua_dl_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/223,1\n"""
        u"""member = SIP/215,2\n"""
        u"""member = SIP/222,3\n"""
        u"""[entrada_cua_dl_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/205,1\n"""
        u"""member = SIP/215,2\n"""
        u"""member = SIP/222,3\n"""
        u"""[entrada_cua_dm_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/218,1\n"""
        u"""member = SIP/206,2\n"""
        u"""member = SIP/217,3\n"""
        u"""[entrada_cua_dm_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/217,1\n"""
        u"""member = SIP/218,2\n"""
        u"""member = SIP/206,3\n"""
        u"""[entrada_cua_dm_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/207,1\n"""
        u"""member = SIP/222,2\n"""
        u"""member = SIP/216,3\n"""
        u"""[entrada_cua_dm_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/204,1\n"""
        u"""member = SIP/207,2\n"""
        u"""member = SIP/203,3\n"""
        u"""[entrada_cua_dx_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/214,1\n"""
        u"""member = SIP/224,2\n"""
        u"""member = SIP/205,3\n"""
        u"""[entrada_cua_dx_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/224,1\n"""
        u"""member = SIP/214,2\n"""
        u"""member = SIP/223,3\n"""
        u"""[entrada_cua_dx_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/203,1\n"""
        u"""member = SIP/202,2\n"""
        u"""member = SIP/218,3\n"""
        u"""[entrada_cua_dx_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/204,1\n"""
        u"""member = SIP/207,2\n"""
        u"""member = SIP/218,3\n"""
        u"""[entrada_cua_dj_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/202,1\n"""
        u"""member = SIP/210,2\n"""
        u"""member = SIP/223,3\n"""
        u"""[entrada_cua_dj_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/215,1\n"""
        u"""member = SIP/207,2\n"""
        u"""member = SIP/210,3\n"""
        u"""[entrada_cua_dj_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/216,1\n"""
        u"""member = SIP/203,2\n"""
        u"""member = SIP/208,3\n"""
        u"""[entrada_cua_dj_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/208,1\n"""
        u"""member = SIP/216,2\n"""
        u"""member = SIP/203,3\n"""
        u"""[entrada_cua_dv_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/206,1\n"""
        u"""member = SIP/218,2\n"""
        u"""member = SIP/202,3\n"""
        u"""[entrada_cua_dv_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/218,1\n"""
        u"""member = SIP/215,2\n"""
        u"""member = SIP/202,3\n"""
        u"""[entrada_cua_dv_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/222,1\n"""
        u"""member = SIP/205,2\n"""
        u"""member = SIP/210,3\n"""
        u"""[entrada_cua_dv_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""
        u"""member = SIP/210,1\n"""
        u"""member = SIP/223,2\n"""
        u"""member = SIP/214,3\n"""
        )

    def test_penalties(self):
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            colors:
              ana: aa11aa
            extensions:
              ana: 1001
            names: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )

        self.assertEqual(h.htmlPenalties(),
            "<h3>Penalitzacions</h3>\n"
            "<p>Sense penalitzacions</p>\n"
        )

    def test_penalties_cost_nopenalties(self):
        cost = 123
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            colors:
              ana: aa11aa
            extensions:
              ana: 1001
            names: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            cost: {}
            """.format(cost))
        )

        self.assertEqual(h.htmlPenalties(),
            "<h3>Penalitzacions</h3>\n"
            "<p>Penalitzacio: {}</p>\n".format(cost)
        )

    def test_penalties_nocost_penalties(self):
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            colors:
              ana: aa11aa
            extensions:
              ana: 1001
            names: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            penalties:
            - - 20
              - pol te dos torns
            - - 30
              - david te una indisponiblitats opcional
            """)
        )

        self.assertEqual(h.htmlPenalties(),
            "<h3>Penalitzacions</h3>\n"
            "<ul>\n"
                "<li>20: pol te dos torns</li>\n"
                "<li>30: david te una indisponiblitats opcional</li>\n"
            "</ul>\n"
            ''
        )

    def test_penalties_cost_penalties(self):
        h=HtmlGen(self.ns("""\
            week: '2016-07-25'
            timetable:
              dl:
              - - ana
            hours:
            - '09:00'
            - '10:15'
            turns:
            - L1
            colors:
              ana: aa11aa
            extensions:
              ana: 1001
            names: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            cost: 123
            penalties:
            - - 20
              - pol te dos torns
            - - 30
              - david te una indisponiblitats opcional
            """)
        )

        self.assertEqual(h.htmlPenalties(),
            "<h3>Penalitzacions</h3>\n"
            "<p>Penalitzacio: 123</p>\n"
            "<ul>\n"
                "<li>20: pol te dos torns</li>\n"
                "<li>30: david te una indisponiblitats opcional</li>\n"
            "</ul>\n"
            ''
        )


if __name__ == "__main__":

    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True
    if 'B2BACCEPT' in sys.env:
        unittest.TestCase.acceptMode = True

    unittest.main()

# vim: ts=4 sw=4 et
