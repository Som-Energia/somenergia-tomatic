# -*- coding: utf-8 -*-
import unittest
from yamlns import namespace as ns

def llegeixHores(yaml):
		lines = [str(h) for h in yaml.hores ]
		return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]

def htmlTable(yaml):
    headerDays=("""<tr>"""
            """<td></td>"""+""
            "".join([
                """<th colspan={colspan}>{day}</th>""".format(
                    colspan=len(yaml.torns),
                    day=day
                    )
                for day in yaml.timetable.keys()
                ])+""
            """</tr>\n""")
    headerTlfnos=("""<tr><td></td>"""
            ""+("".join(["<th>{}</th>".format(t) for t in yaml.torns]))+"</tr>\n")
    dayTable=("</tr>\n".join([
                """<tr><th>{period}</th>\n""".format(period=period)+""
                "\n".join([
                    """<td class='{name}'>"""
                    """{properName}</td>""".format(
                        name=name,
                        properName=name.title())
                        for name in yaml.timetable.dl[turn+1]])+"\n"
                 for turn,period in enumerate(llegeixHores(yaml))
                 ])+""
            """</tr>\n""")
    return( """<table>\n"""
            ""+headerDays+headerTlfnos+dayTable+""
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

# vim: ts=4 sw=4 et
