# -*- coding: utf-8 -*-
import random
from yamlns import namespace as ns

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
    def htmlExtensions(self):
        header =(u"""<h3>Extensions</h3>\n"""
                u"""<div class="extensions">\n""")
        footer = u"""</div>"""
        if 'extensions' in self.yaml:
            extensions = sorted(self.yaml.extensions.items(),
                key=lambda e:e[0])
            body = ("\n".join([(u"""<div class="extension {}">"""
                             u"""{}<br/>{}</div>""").format(
                                name,
                                self.properName(name),
                                extension)
                            for (name,extension) in extensions])+""
                   "\n")
        else:
            body = ""
        return header+body+footer
    
    def htmlSetmana(self):
        if 'setmana' in self.yaml:
            setmanaHeader = ("<h1>"
                             "Setmana {}".format(self.yaml.setmana)+""
                             "</h1>")
        else:
            setmanaHeader = "<h1>Setmana ???</h1>"
        return setmanaHeader
    
    def htmlColors(self):
        colors= "\n".join(
            ".{} {{ background-color: #{}; }}".format(
                nom,
                self.yaml.colors[nom]
                if 'colors' in self.yaml and nom in self.yaml.colors
                    and not ('randomColors' in self.yaml
                    and self.yaml.randomColors)
                else
                    "{:02x}{:02x}{:02x}".format(
                    random.randint(127,255),
                    random.randint(127,255),
                    random.randint(127,255),
                    )
                )
            for nom in self.yaml.companys
            )
        return colors
    def htmlHeader(self):
        return  (u"""<!doctype html>\n"""
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
            u"""}\n"""
            )
    def htmlSubHeader(self):
        return (u"""\n</style>\n</head>\n"""
                     u"""<body>\n"""
                     )
    def htmlFooter(self):
        return  u"""</body>\n</html>"""

    def htmlParse(self):
        return (self.htmlHeader()+
            self.htmlColors()+
            self.htmlSubHeader()+
            self.htmlSetmana()+self.htmlTable()+
            self.htmlExtensions()+
            self.htmlFixExtensions()+
            self.htmlFooter()
        )
    def htmlPenalizations(self,minimumCost,penalties):
        return  '\n'.join([
            "",
            "<p>Penalitzacio: {}</p>".format(minimumCost),
            "<ul>",
            "\n".join(
                "<li>{}: {}</li>".format(*reason)
                for reason in penalties
            ),
            "</ul>",
            '',
        ])

    def htmlFixExtensions(self):
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
        with open("extensions.html") as extensions_html:
            extensions = extensions_html.read()
        return extensions

class HtmlGenFromYaml(HtmlGen):
    def __init__(self, yaml):
        self.yaml = yaml
        
class HtmlGenFromSolution(HtmlGen):

    def iniciSetmana(self, date=None):
        from datetime import date as dateModule, timedelta
        import datetime
        if date is None:
            # If no date provided, take the next monday
            today = dateModule.today()
            return today + timedelta(days=7-today.weekday())
        # take the monday of the week including that date
        #givenDate = datetime.datetime.strptime(date,"%Y-%m-%d").date()
        return date - timedelta(days=date.weekday())

    def getYaml(self):
        return self.yaml
    
    def __init__(self, config, solution, companys=None, date=None):
        y = ns(zip(
            config.diesVisualitzacio,
            [ns() for i in range(len(config.diesVisualitzacio))]))
        nhores = len(config.hores)-1
        for d in y:
            for h in range(nhores):
                y[d][h+1]=[None]*config.nTelefons 
        for day in config.diesVisualitzacio:
            for turn in range(nhores):
                for tel in range(config.nTelefons):
                    y[day][turn+1][tel]=solution.get(
                        (day,turn,tel),
                        'festiu'
                    ).lower()
        y=ns({'timetable': y})
        y['hores']=config.hores
        y['torns']= ["T"+str(i+1) for i in range(config.nTelefons)]
        y['colors']=config.colors
        y['extensions']=config.extensions
        y['setmana']=self.iniciSetmana(date)
        y['noms']=config.noms
        y['companys']=companys
        #with open("graella-"+str(iniciSetmana())+".yaml",'w') as output:
        #    output.write(y.dump().decode('utf-8'))
        self.yaml=y
