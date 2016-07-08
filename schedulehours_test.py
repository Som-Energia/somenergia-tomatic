# -*- coding: utf-8 -*-
import unittest
from yamlns import namespace as ns

def htmlTable(yaml):
    return(
            """<table>\n"""
            """<tr>"""
            """<td></td><th colspan={colspan}>dl</th>""".format(
                colspan=len(yaml.torns)
                )+""
            """</tr>\n"""
            """<tr><td></td>"""
            ""+("".join(["<th>{}</th>".format(t) for t in yaml.torns]))+""
            """</tr>\n"""
            """<tr><th>{period}</th>\n"""+""
            "\n".join([
                """<td class='{name}'>"""
                """{properName}</td>""".format(
                    name=name,
                    properName=name.title())
                    for name in yaml.timetable.dl[1]])+"\n"
            """</tr>\n"""
            """</table>"""
            ).format(
                name=yaml.timetable.dl[1][0],
                properName=yaml.timetable.dl[1][0].title(),
                period="-".join(yaml.hores[0:2])
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
        

# vim: ts=4 sw=4 et
