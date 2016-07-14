# -*- coding: utf-8 -*-
import unittest
from yamlns import namespace as ns
import b2btest
import sys
from parse import parse
import random

def properName(name,yaml):
    name = yaml.noms[name] if name in yaml.noms else name
    return name.title()
    

def llegeixHores(yaml):
		lines = [str(h) for h in yaml.hores ]
		return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]
def htmlParse(yaml):
    header = (u"""<!doctype html>\n"""
        u"""<html>\n"""
        u"""<head>\n"""
        u"""<meta charset='utf-8' />\n"""
        u"""<style>\n"""
        u"""h1 {\n"""
        u"""    color: #560;\n"""
        u"""}\n"""
        u"""td, th {\n"""
        u"""	border:1px solid black;\n"""
        u"""	width: 8em;\n"""
        u"""	text-align: center;\n"""
        u"""}\n"""
        u"""td:empty { border:0;}\n"""
        u"""td { padding: 1ex;}\n"""
        u""".extensions { width: 60%; }\n"""
        u""".extension {\n"""
        u"""	display: inline-block;\n"""
        u"""	padding: 1ex 0ex;\n"""
        u"""	width: 14%;\n"""
        u"""	text-align: center;\n"""
        u"""	margin: 2pt 0pt;\n"""
        u"""	border: 1pt solid black;\n"""
        u"""	height: 100%;\n"""
        u"""}\n""")
    subheader = (u"""\n</style>\n</head>\n"""
                 u"""<body>\n""")
    footer = u"""</body>\n</html>"""
    return (header+htmlColors(yaml)+subheader
        +htmlSetmana(yaml)+htmlTable(yaml)+
        htmlExtensions(yaml)+
        htmlFixExtensions()+footer)
def htmlFixExtensions():
    return (u"""<div class="extensions">\n"""
            u"""<div class="extension """
            u"""gijsbert">Inalàmbric<br/>3385</div>\n"""
            u"""<div class="extension recepcio">"""
            u"""Recepcio<br/>3405</div>\n"""
            u"""</div>\n"""
            u"""<h3>Recordatori desviaments</h3>\n"""
            u"""<ul>\n"""
            u"""<li>*60 Immediat</li>\n"""
            u"""<li>*63 Ocupat o no responem</li>\n"""
            u"""<li>*64 Treure desviaments</li>\n"""
            u"""<li>*90 Marcar número</li>\n"""
            u"""</ul>\n"""
            )
def htmlColors(yaml):
    colors= "\n".join(
        ".{} {{ background-color: #{}; }}".format(
            nom,
            yaml.colors[nom]
            if 'colors' in yaml and nom in yaml.colors
            else
                "{:02x}{:02x}{:02x}".format(
                random.randint(127,255),
                random.randint(127,255),
                random.randint(127,255),
                )
            )
        for nom in yaml.companys
        )
    return colors


def htmlSetmana(yaml):
    if 'setmana' in yaml:
        setmanaHeader = ("<h1>"
                         "Setmana {}".format(yaml.setmana)+""
                         "</h1>")
    else:
        setmanaHeader = "<h1>Setmana ???</h1>"
    return setmanaHeader

def htmlExtensions(yaml):
    header =(u"""<h3>Extensions</h3>\n"""
            u"""<div class="extensions">\n""")
    footer = u"""</div>"""
    if 'extensions' in yaml:
        extensions = sorted(yaml.extensions.items(),
            key=lambda e:e[0])
        body = ("\n".join([(u"""<div class="extension {}">"""
                         u"""{}<br/>{}</div>""").format(
                            name,
                            properName(name,yaml),
                            extension)
                        for (name,extension) in extensions])+""
               "\n")
    else:
        body = ""
    return header+body+footer

def htmlTable(yaml):
    def properName(name,yaml=yaml):
        global properName
        return properName(name,yaml)

    def partialCoreTable(day,turn):
        return "\n".join([
                u"""<td class='{name}'>"""
                u"""{properName}</td>""".format(
                    name=name,
                    properName=properName(name))
                    for name in yaml.timetable[day][turn+1]])+"\n"
    headerDays=("""<tr>"""+""
            "".join([
                """<td></td><th colspan={colspan}>{day}</th>""".format(
                    colspan=len(yaml.torns),
                    day=day
                    )
                for day in yaml.timetable.keys()
                ])+""
            """</tr>\n""")
    headerTlfnos=("""<tr>"""+("""<td></td>"""
            ""+("".join([
                         "<th>{}</th>".format(t) 
                         for t in yaml.torns
                         ])))*len(yaml.timetable.keys())+""
            "</tr>\n")
    coreTable=("</tr>\n".join([
                """<tr><th>{period}</th>\n""".format(
                    period=period)+"<td>&nbsp;</td>\n".join(
                        [partialCoreTable(day,turn) for day in yaml.timetable.keys()
                        ])
                 for turn,period in enumerate(llegeixHores(yaml))
                 ])+""
            """</tr>\n""")
    return( """<table>\n"""
            ""+headerDays+headerTlfnos+coreTable+""
            """</table>"""
            )

class ScheduleHours_Test(unittest.TestCase):
    def ns(self,content):
        return ns.loads(content)
    
    def test_htmlTable_oneslot(self):

        inputyaml=self.ns("""\
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

        self.assertMultiLineEqual(
            htmlTable(inputyaml), 
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=1>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
    def test_htmlTable_twoTelephonesOneTurnOneDay(self):
        inputyaml=self.ns("""\
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
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
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
        inputyaml=self.ns("""\
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
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
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
        inputyaml=self.ns("""\
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
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
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
        inputyaml=self.ns("""\
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
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
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
        yaml = ("""\
            extensions:
               marta:  3040
            noms:
               cesar: César
               """)
        nsyaml = self.ns(yaml)    
        self.assertMultiLineEqual(htmlExtensions(nsyaml),"""<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")
    
    def test_htmlExtension_twoExtensions(self):
        yaml = ("""\
            extensions:
               marta:  3040
               aleix:  3053
            noms:
               cesar: César
               """)
        nsyaml = self.ns(yaml)    
        self.assertMultiLineEqual(htmlExtensions(nsyaml),"""<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """<div class="extension aleix">Aleix<br/>3053</div>\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")

    def test_htmlExtension_noExtensions(self):
        yaml = ("""\
            noms:
               cesar: César
               """)
        nsyaml = self.ns(yaml)    
        self.assertMultiLineEqual(htmlExtensions(nsyaml),"""<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """</div>""")

    def test_htmlHeader_properSetmana(self):
        yaml = ("""\
            setmana: 2016-07-25
                """)
        nsyaml = self.ns(yaml)
        self.assertMultiLineEqual(htmlSetmana(nsyaml),"""<h1>Setmana 2016-07-25</h1>""")

    def test_htmlHeader_noSetmana(self):
        yaml = ("""\
            noms:
               cesar: César
                """)
        nsyaml = self.ns(yaml)
        self.assertMultiLineEqual(htmlSetmana(nsyaml),"""<h1>Setmana ???</h1>""")

    def test_htmlColors_oneColor(self):
        yaml = ("""\
            colors:
               marc: fbe8bc
            companys:
            - marc
                """)
        nsyaml = self.ns(yaml)
        self.assertMultiLineEqual(htmlColors(nsyaml),
            """.marc { background-color: #fbe8bc; }""")

    def test_htmlColors_randomColor(self):
        yaml = ("""\
            companys:
            - cesar
                """)
        nsyaml = self.ns(yaml)
        self.assertRegexpMatches(parse(
            """.cesar {{ background-color: {} }}""",
                  htmlColors(nsyaml)
                  )[0],
            '#[0-9a-f]{6};'

        )

    def test_htmlParse_completeHtml(self):
       self.maxDiff = None
       inputyaml = ("""\
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
       nsyaml = self.ns(inputyaml)
       self.b2bdatapath = "testcases"
       self.assertB2BEqual(htmlParse(nsyaml).encode('utf-8'))

if __name__ == "__main__":

    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True
    
    unittest.main()
# vim: ts=4 sw=4 et
