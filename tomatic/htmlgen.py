# -*- coding: utf-8 -*-
import random
import datetime
from yamlns import namespace as ns

class HtmlGen(object):

    @staticmethod
    def iniciSetmana(date=None):
        from datetime import date as dateModule, timedelta
        import datetime
        if date is None:
            # If no date provided, take the next monday
            today = dateModule.today()
            return today + timedelta(days=7-today.weekday())
        # take the monday of the week including that date
        return date - timedelta(days=date.weekday())

    def properName(self,name):
        name = self.yaml.names[name] if name in self.yaml.names else name
        return name.title()

    def llegeixHores(self):
        lines = [str(h) for h in self.yaml.hours ]
        return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]

    def partialCoreTable(self,day,turn):
        return "".join([
            u"""<td class='{name}'>{properName}</td>\n"""
            .format(
                name=name,
                properName=self.properName(name)
            )
            for name in self.yaml.timetable[day][turn+1]
            ])

    def partialCurrentQueue(self,day,turn):
        hours = (
            "<tr><th>"+""
            ""+self.llegeixHores()[turn-1]+""
            "</th>\n"
        )
        partialCoreTable = self.partialCoreTable(day,turn-1)
        header=(
            """<table>\n"""
            """<tr>"""
            """<td></td><th colspan="100%">{day}</th>"""
            """</tr>\n"""
            .format(
                 day=day
                 )
        )
        headerTlfnos=''.join([
            '<tr>'
            '<td></td>'
            ]+[
            '<th>{}</th>'.format(t)
            for t in self.yaml.turns
            ]+(
            [u'<th colspan="100%">Cua dinàmica</th>']
            if "dynamic" in self.yaml else []
            )+[
            '</tr>\n'
            ]
        )
        footer= u"""</tr>\n</table>"""
        partialDynamicTable= self.partialDynamicTable() if "dynamic" in self.yaml else ""
        return header+headerTlfnos+hours+partialCoreTable+partialDynamicTable+footer

    def partialDynamicTable(self):
        return "\n".join([
                u"""<td class='{name}'>"""
                u"""{properName}</td>""".format(
                    name=name,
                    properName=self.properName(name))
                    for name in self.yaml.dynamic])+"\n"    

    def htmlTable(self):
        headerDays=(
            """<tr>"""+
            "".join([
                """<td></td><th colspan={colspan}>{day}</th>"""
                    .format(
                        colspan=len(self.yaml.turns),
                        day=day
                        )
                for day in self.yaml.timetable.keys()
                ])+
            """</tr>\n"""
            )
        ndays = len(self.yaml.timetable)
        headerTlfnos="".join([
            """<tr>""",(
            """<td></td>"""
            +(
                "".join([
                    "<th>{}</th>".format(t) 
                    for t in self.yaml.turns
                ])
            ))*ndays +
            "</tr>\n"
            ])
        coreTable=(
            "</tr>\n".join(
                """<tr><th>{period}</th>\n""".format(period=period)+
                    "<td>&nbsp;</td>\n".join(
                        self.partialCoreTable(day,turn)
                        for day in self.yaml.timetable.keys()
                        )
                    for turn,period in enumerate(self.llegeixHores()
                    )
                )+""
            """</tr>\n""")
        return ''.join([
            """<table>\n""",
            headerDays,
            headerTlfnos,
            coreTable,
            """</table>""",
            ])

    def htmlExtensions(self):
        header =(
            u"""<h3>Extensions</h3>\n"""
            u"""<div class="extensions">\n"""
            )
        footer = u"""</div>"""
        if 'extensions' in self.yaml:
            extensions = sorted(self.yaml.extensions.items())
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
        if 'week' in self.yaml:
            setmanaHeader = ("<h1>"
                             "Setmana {}".format(self.yaml.week)+""
                             "</h1>")
        else:
            setmanaHeader = "<h1>Setmana ???</h1>"
        return setmanaHeader

    def colorFor(self, name):
        def randomColor():
            return "{:02x}{:02x}{:02x}".format(
                random.randint(127,255),
                random.randint(127,255),
                random.randint(127,255),
                )

        if 'colors' not in self.yaml:
            self.yaml.colors=ns()

        if self.yaml.get('randomColors',False):
            self.yaml.colors[name] = randomColor()
        elif name not in self.yaml.colors:
            self.yaml.colors[name] = randomColor()

        return self.yaml.colors[name]

    def htmlColors(self):
        for name in self.yaml.get('extensions',[]):
            self.colorFor(name)
        for name in self.yaml.get('names',[]):
            self.colorFor(name)
        colors= "\n".join(
            ".{:<8} {{ background-color: #{}; }}".format(nom, color)
            for nom, color in sorted(self.yaml.colors.items())
            )
        return colors

    def htmlHeader(self):
        return  (
            u"""<!doctype html>\n"""
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
            u""".extensions { width: 60%;}\n"""
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
        return (
            u"""\n</style>\n</head>\n"""
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
        extensions_inv = {
            extension : name
            for name, extension in self.yaml.extensions.items()
            }
        return extensions_inv[extension]

    def asteriskParse(self):
        common = [
            'music=default',
            'strategy=linear',
            'eventwhencalled=yes',
            'timeout=15',
            'retry=1',
            'wrapuptime=0',
            'maxlen = 0',
            '; Periodic-announce = /var/lib/asterisk/sounds/bienvenida',
            'Periodic-announce-frequency = 15',
            'announce-frequency = 0',
            'announce-holdtime = no',
            'announce-position =no',
            'context = bustia_veu',
        ]
        r = []
        tt = self.yaml.timetable
        ext = self.yaml.extensions
        for d in tt.keys():
            for t in tt[d].keys():
                r+=[u"[entrada_cua_{}_{}]".format(
                    d,t)]
                r+=common
                for index,m in enumerate(tt[d][t]):
                    r+=[(u"member = SIP/{},{}"
                        ).format(ext[m],index+1)]
        return u'\n'.join(r)+u'\n'

    def getCurrentQueue(self,now):
        # Supposes ordered "hours" list (less to greater)
        dowInt = now.isoweekday()
        dowDict = {
            1:'dl',
            2:'dm',
            3:'dx',
            4:'dj',
            5:'dv'
            }
        if dowInt not in dowDict:
            raise Exception
        else:
            day = dowDict[dowInt]
        parsedTimeIntervals = [
            datetime.datetime(
                now.year,
                now.month,
                now.day,
                int(hour[0:2]),
                int(hour[3:5])
            )
            for hour 
            in self.yaml.hours]
        if now < parsedTimeIntervals[0]:
            raise Exception
        for turn,hour in enumerate(parsedTimeIntervals[1:]):
            if now < hour:
                break
        return day,turn+1

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
        def getDynamicPaused(yaml):
            if ("paused" 
                in yaml and
                "dynamic"
                in yaml.paused):
                return set(
                    yaml.paused.dynamic)
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
        selfDynamicPaused = getDynamicPaused(
            self.yaml)
        otherDynamicPaused = getDynamicPaused(
            other.yaml)
        added_dynamic = otherDynamicPaused - selfDynamicPaused
        removed_dynamic = selfDynamicPaused - otherDynamicPaused 
        response = ns()
        if added_dynamic or removed_dynamic:
            response.dynamic = ns()
        for name in added_dynamic:
            ext = self.nameToExtension(name)
            response.dynamic[ext]="added"

        for name in removed_dynamic:
            ext = self.nameToExtension(name)
            response.dynamic[ext]="removed"

        for day in self.yaml.timetable:
            for turn in self.yaml.timetable[day]:
                for name in self.yaml.colors.keys():
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
        for name in self.yaml.colors.keys():
            if name in added:
                ext = self.nameToExtension(name)
                response[ext]="added"
        for name in self.yaml.colors.keys():
            if name in removed:
                ext = self.nameToExtension(name)
                response[ext]="removed"
        return response



class HtmlGenFromSolution(HtmlGen):

    def __init__(self, config, solution, date=None):
        y = ns(zip(
            config.diesVisualitzacio,
            [ns() for i in range(len(config.diesVisualitzacio))]))
        nhours = len(config.hours)-1
        for d in y:
            for h in range(nhours):
                y[d][h+1]=[None]*config.nTelefons 
        for day in config.diesVisualitzacio:
            for turn in range(nhours):
                for tel in range(config.nTelefons):
                    y[day][turn+1][tel]=solution.get(
                        (day,turn,tel),
                        'festiu'
                    ).lower()
        y=ns({'timetable': y})
        y['hours']=config.hours
        y['turns']= ["T"+str(i+1) for i in range(config.nTelefons)]
        y['colors']=config.colors
        y['extensions']=config.extensions
        y['week']=str(self.iniciSetmana(date))
        y['names']=config.names
        # TODO: include days
        #y.days="dl dm dx dj dv".split()
        self.yaml=y



class HtmlGenFromAsterisk(HtmlGenFromSolution):
    # Only linear queues are implemented at the moment
    def __init__(self, yaml, asteriskConf):
        asteriskQueues = {
            (k.split('_')[-2], 
                int(k.split('_')[-1])
            ): [ (ext,asteriskConf[k]
                    ['members'][ext]
                    ['Penalty']
                 )  for ext 
                    in asteriskConf[k][
                        'members'].keys()
               ]
            for k in asteriskConf.keys() 
                if 'dinamica' not in k
        }
        asteriskPaused = {
            (k.split('_')[-2], 
                int(k.split('_')[-1])
            ): [asterisk_sip for asterisk_sip in
                asteriskConf[k]['members'].keys()
                if asteriskConf[k]['members'][asterisk_sip]['Paused']=='1']
            for k in asteriskConf.keys()
                if 'dinamica' not in k
        }
        asteriskDynamic = [ext
            for ext 
            in asteriskConf['entrada_dinamica']['members'].keys()
        ] if 'entrada_dinamica' in asteriskConf else []

        extensions_inv = { extension : name for name, extension in yaml.extensions.items()}
        solution_asterisk = {}
        solution_paused = {}
        for q in asteriskQueues:
            asteriskQueue = [
                extensions_inv[
                    int(ext_sip.split('/')[1])]
                for ext_sip,_ in sorted(
                    asteriskQueues[q],
                    key=lambda ext:ext[1])]
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
        dynamic = [
            extensions_inv[
                int(ext_sip.split('/')[1])]
            for ext_sip 
            in asteriskDynamic
        ]
        y = ns()
        y.dynamic = dynamic
        y.timetable = tt_asterisk
        y.paused = paused
        y.names = yaml.names
        y.hours = yaml.hours
        y.turns = yaml.turns
        y.colors = yaml.colors
        y.extensions = yaml.extensions
        y.week = yaml.week
        self.yaml=y

def asteriskConfiguration(schedule):
    h = HtmlGenFromYaml(schedule)
    return h.asteriskParse()

# vim: et
