# -*- coding: utf-8 -*-
class HtmlGen(object):

    def properName(self,name):
        name = self.yaml.noms[name] if name in self.yaml.noms else name
        return name.title()


    def llegeixHores(self):
        lines = [str(h) for h in self.yaml.hores ]
        return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]

    def htmlTable(self):
        def partialCoreTable(day,turn):
            return "\n".join([
                    u"""<td class='{name}'>"""
                    u"""{properName}</td>""".format(
                        name=name,
                        properName=self.properName(name))
                        for name in self.yaml.timetable[day][turn+1]])+"\n"
        headerDays=("""<tr>"""+""
                "".join([
                    """<td></td><th colspan={colspan}>{day}</th>""".format(
                        colspan=len(self.yaml.torns),
                        day=day
                        )
                    for day in self.yaml.timetable.keys()
                    ])+""
                """</tr>\n""")
        headerTlfnos=("""<tr>"""+("""<td></td>"""
                ""+("".join([
                             "<th>{}</th>".format(t) 
                             for t in self.yaml.torns
                             ])))*len(self.yaml.timetable.keys())+""
                "</tr>\n")
        coreTable=("</tr>\n".join([
                    """<tr><th>{period}</th>\n""".format(
                        period=period)+"<td>&nbsp;</td>\n".join(
                            [partialCoreTable(day,turn) for day in self.yaml.timetable.keys()
                            ])
                     for turn,period in enumerate(self.llegeixHores())
                     ])+""
                """</tr>\n""")
        return( """<table>\n"""
                ""+headerDays+headerTlfnos+coreTable+""
                """</table>"""
                )
