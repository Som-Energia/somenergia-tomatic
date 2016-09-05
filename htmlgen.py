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
            u""".paused { background-color"""
            u""": #ffffff; }\n"""
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
    
    def nameToExtension(self, name):
        return self.yaml.extensions[name]

    def extensionToName(self, extension):
        extensions_inv = { extension : name for name, extension in self.yaml.extensions.items()}
        return extensions_inv[extension]

    def asteriskParse(self):
        header = (u"""music=default\n"""
                  u"""strategy=rrmemory\n"""
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
                  u"""context = bustia_veu\n""")
        r = u""
        tt = self.yaml.timetable
        ext = self.yaml.extensions
        for d in tt.keys():
            for t in tt[d].keys():
                r+=u"[entrada_cua_{}_{}]\n".format(
                    d,t)
                r+=header
                for m in tt[d][t]:
                    r+=(u"member = SIP/{}\n"
                        ).format(ext[m])
        return r


    def getYaml(self):
        return self.yaml

class HtmlGenFromYaml(HtmlGen):
    def __init__(self, yaml):
        self.yaml = yaml
        
    def comparePaused(self, other):
        def getPaused(yaml,day,turn):
            if ("paused" 
                in yaml and
                day
                in yaml.paused and
                turn
                in yaml.paused[day]):
                return set(
                    yaml.paused[day][turn])
            else:
                return set()
            
        added = set()
        removed = set()
        for day in self.yaml.timetable:
            for turn in self.yaml.timetable[day]:
                selfPaused = getPaused(
                    self.yaml,day,turn)
                otherPaused = getPaused(
                    other.yaml,day,turn)
                removedInTurn = selfPaused - otherPaused
                addedInTurn = otherPaused - selfPaused
                for name in addedInTurn:
                    added.add((day,turn,name))
                for name in removedInTurn:
                    removed.add((day,turn,name))
        response = ns()
        for day in self.yaml.timetable:
            for turn in self.yaml.timetable[day]:
                for name in self.yaml.companys:
                    if (day,turn,name) in added:
                       if day not in response:
                           response[day]=ns()
                       if turn not in response[
                           day]:
                           response[day][turn]=ns()
                       ext = self.nameToExtension(name)
                       response[day][turn][ext]="added"
                    if (day,turn,name) in removed:
                       if day not in response:
                           response[day]=ns()
                       if turn not in response[
                           day]:
                           response[day][turn]=ns()
                       ext = self.nameToExtension(name)
                       response[day][turn][ext]="removed"

        return response
    def compareDynamic(self, other):
        response = ns()
        if "dynamic" not in other.yaml:
            added = set()
            removed = set(self.yaml.dynamic)
        elif "dynamic" not in self.yaml:
            removed = set()
            added = set(other.yaml.dynamic)
        else:
            added = set(other.yaml.dynamic
                ) - set(self.yaml.dynamic)
            removed = set(self.yaml.dynamic
                ) - set(other.yaml.dynamic)
        for name in self.yaml.companys:
            if name in added:
                ext = self.nameToExtension(name)
                response[ext]="added"
        for name in self.yaml.companys:
            if name in removed:
                ext = self.nameToExtension(name)
                response[ext]="removed"
        return response
        
class HtmlGenFromSolution(HtmlGen):

    def iniciSetmana(self, date=None):
        from datetime import date as dateModule, timedelta
        import datetime
        if date is None:
            # If no date provided, take the next monday
            today = dateModule.today()
            return today + timedelta(days=7-today.weekday())
        # take the monday of the week including that date
        return date - timedelta(days=date.weekday())

    
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
        self.yaml=y

class HtmlGenFromAsterisk(HtmlGenFromSolution):
    # Only rrmemory policy queue is implemented
#   # Because queues are not ordered yet.
    
    def __init__(self, yaml, asteriskConf):
        asteriskQueues = {
            (k.split('_')[-2], 
                int(k.split('_')[-1])
            ): asteriskConf[k]['members'].keys()
            for k in asteriskConf.keys() 
        }
        asteriskPaused = {
            (k.split('_')[-2], 
                int(k.split('_')[-1])
            ): [asterisk_sip for asterisk_sip in
                asteriskConf[k]['members'].keys()
                if asteriskConf[k]['members'][asterisk_sip]['Paused']=='1']
            for k in asteriskConf.keys()
        }

        extensions_inv = { extension : name for name, extension in yaml.extensions.items()}
        solution_asterisk = {}
        solution_paused = {}
        for q in asteriskQueues:
            asteriskQueue = [extensions_inv[int(ext_sip.split('/')[1])] 
                for ext_sip in asteriskQueues[q]]
            for nTel, name in enumerate(asteriskQueue):
                solution_asterisk[(q[0],q[1],nTel)]=name
        for q in asteriskPaused:
            asteriskPausedSingle = [extensions_inv[int(ext_sip.split('/')[1])] 
                for ext_sip in asteriskPaused[q]]
            for nTel, name in enumerate(asteriskPausedSingle):
                solution_paused[(q[0],q[1],nTel)]=name
        tt_yaml = yaml.timetable
        paused = ns()
        tt_asterisk = ns()
        for day in { k[0] for k in solution_asterisk}:
            tt_asterisk[day] = ns()
            paused[day] = ns()
            for turn in {k[1] for k in solution_asterisk if k[0]==day}:
                tt_asterisk[day][turn] = []
                paused[day][turn] = []
                for tel in {k[2] for k in solution_asterisk if k[0]==day and k[1]==turn}:
                    tt_asterisk[day][turn].append(
                        solution_asterisk.get(
                            (day,
                            turn,
                            tel),'Error')
                    )
                    if (day,turn,tel) in solution_paused:
                        paused[day][turn].append(
                            solution_paused[
                                (day,
                                turn,
                                tel)])
        y = ns()
        y.timetable = tt_asterisk
        y.paused = paused
        y.hores = yaml.hores
        y.torns = yaml.torns
        y.colors = yaml.colors
        y.extensions = yaml.extensions
        y.setmana = yaml.setmana
        y.companys = yaml.companys
        self.yaml=y
