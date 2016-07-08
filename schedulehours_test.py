# -*- coding: utf-8 -*-
import unittest
from yamlns import namespace as ns

def llegeixHores(yaml):
		lines = [str(h) for h in yaml.hores ]
		return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]
def htmlTable(yaml):
    def partialCoreTable(day,turn):
        return "\n".join([
                """<td class='{name}'>"""
                """{properName}</td>""".format(
                    name=name,
                    properName=name.title())
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

        inputyaml=self.ns(u"""\
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
            """)

        self.assertMultiLineEqual(
            htmlTable(inputyaml), 
            """<table>\n"""
            """<tr><td></td><th colspan=1>dl</th></tr>\n"""
            """<tr><td></td><th>T1</th>"""
            """</tr>\n"""
            """<tr><th>09:00-10:15</th>\n"""
            """<td class='ana'>Ana</td>\n"""
            """</tr>\n"""
            """</table>""")
    def test_htmlTable_twoTelephonesOneTurnOneDay(self):
        inputyaml=self.ns(u"""\
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
            """)
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
            """<table>\n"""
            """<tr><td></td><th colspan=2>dl</th></tr>\n"""
            """<tr><td></td><th>T1</th><th>T2</th>"""
            """</tr>\n"""
            """<tr><th>09:00-10:15</th>\n"""
            """<td class='ana'>Ana</td>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """</tr>\n"""
            """</table>""")
        
    def test_htmlTable_twoTelephonesTwoTurnsOneDay(self):
        inputyaml=self.ns(u"""\
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
            """)
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
            """<table>\n"""
            """<tr><td></td><th colspan=2>dl</th></tr>\n"""
            """<tr><td></td><th>T1</th><th>T2</th>"""
            """</tr>\n"""
            """<tr><th>09:00-10:15</th>\n"""
            """<td class='ana'>Ana</td>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """</tr>\n"""
            """<tr><th>10:15-11:30</th>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """<td class='aleix'>Aleix</td>\n"""
            """</tr>\n"""
            """</table>""")

    def test_htmlTable_twoTelephonesTwoTurnsTwoDays(self):
        self.maxDiff = None
        inputyaml=self.ns(u"""\
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
            """)
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
            """<table>\n"""
            """<tr><td></td><th colspan=2>dl</th><td></td><th colspan=2>dm</th>"""
            """</tr>\n"""
            """<tr><td></td><th>T1</th><th>T2</th><td></td><th>T1</th><th>T2</th>"""
            """</tr>\n"""
            """<tr><th>09:00-10:15</th>\n"""
            """<td class='ana'>Ana</td>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """<td>&nbsp;</td>\n"""
            """<td class='victor'>Victor</td>\n"""
            """<td class='marta'>Marta</td>\n"""
            """</tr>\n"""
            """<tr><th>10:15-11:30</th>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """<td class='aleix'>Aleix</td>\n"""
            """<td>&nbsp;</td>\n"""
            """<td class='ana'>Ana</td>\n"""
            """<td class='victor'>Victor</td>\n"""
            """</tr>\n"""
            """</table>""")
    
    def _test_htmlTable_manyTelephonesmanyTurnsmanyDays(self):
        self.maxDiff = None
        inputyaml=self.ns(u"""\
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
            """)
        self.assertMultiLineEqual(
            htmlTable(inputyaml),
            """<table>\n"""
            """<tr><td></td><th colspan=3>dl</th>"""
            """<td></td><th colspan=3>dm</th>"""
            """<td></td><th colspan=3>dx</th>"""
            """<td></td><th colspan=3>dj</th>"""
            """<td></td><th colspan=3>dv</th><tr>"""
            """<tr><td></td><th>T1</th><th>T2</th>"""
            """</tr>\n"""
            """<tr><th>09:00-10:15</th>\n"""
            """<td class='ana'>Ana</td>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """<td>&nbsp;</td>\n"""
            """<td class='victor'>Victor</td>\n"""
            """<td class='marta'>Marta</td>\n"""
            """</tr>\n"""
            """<tr><th>10:15-11:30</th>\n"""
            """<td class='jordi'>Jordi</td>\n"""
            """<td class='aleix'>Aleix</td>\n"""
            """<td>&nbsp;</td>\n"""
            """<td class='ana'>Ana</td>\n"""
            """<td class='victor'>Victor</td>\n"""
            """</tr>\n"""
            """</table>""")
# vim: ts=4 sw=4 et
