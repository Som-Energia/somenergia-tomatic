# -*- coding: utf-8 -*-
import unittest
from yamlns import namespace as ns

def htmlTable(yaml):
    return(
            """<table>\n"""
            """<tr><td></td><th colspan=1>dl</th></tr>\n"""
            """<tr><td></td><th>T1</th>\n"""
            """</tr>\n"""
            """<tr><th>{period}</th>\n"""
            """<td class='{name}'>{properName}</td>\n"""
            """</tr>\n"""
            """</table>"""
            ).format(
                name=yaml.timetable.dl[1][0],
                properName=yaml.timetable.dl[1][0].title(),
                period="-".join(yaml.hores[0:2])
                )
    return """\
<table>
<tr><td></td><th colspan=1>dl</th></tr>
<tr><td></td><th>T1</th>
</tr>
<tr><th>09:00-10:15</th>
<td class='ana'>Ana</td>
</tr>
</table>"""



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
            """<tr><td></td><th>T1</th>\n"""
            """</tr>\n"""
            """<tr><th>09:00-10:15</th>\n"""
            """<td class='ana'>Ana</td>\n"""
            """</tr>\n"""
            """</table>"""
)


# vim: ts=4 sw=4 et
