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

    def intervals(self):
        lines = [str(h) for h in self.yaml.hours ]
        return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]

    def partialCoreTable(self,day,time):
        return "".join([
            u"""<td class='{name}'>{properName}</td>\n"""
            .format(
                name=name,
                properName=self.properName(name)
            )
            for name in self.yaml.timetable[day][time]
            ])

    def partialCurrentQueue(self,day,time):
        hours = (
            "<tr><th>"+""
            ""+self.intervals()[time-1]+""
            "</th>\n"
        )
        partialCoreTable = self.partialCoreTable(day,time)
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
            "<tr>"+
            "".join(
                "<td></td><th colspan={colspan}>{day}</th>"
                .format(
                    colspan=len(self.yaml.turns),
                    day=day,
                    )
                for day in self.yaml.timetable.keys()
                )+
            "</tr>\n"
            )
        ndays = len(self.yaml.timetable)
        headerTlfnos="".join([
            "<tr>",(
            "<td></td>"
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
                "<tr><th>{period}</th>\n".format(period=period)+
                "<td>&nbsp;</td>\n".join(
                    self.partialCoreTable(day,time)
                    for day in self.yaml.timetable.keys()
                    )
                for time,period in enumerate(self.intervals()
                )
            )+
            "</tr>\n")
        return ''.join([
            "<table>\n",
            headerDays,
            headerTlfnos,
            coreTable,
            "</table>",
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
            self.htmlSetmana()+
            self.htmlTable()+
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
                u"""<div class="extension gijsbert">"""
                u"""Inalàmbric<br/>3385</div>\n"""
                u"""<div class="extension recepcio">"""
                u"""Recepcio<br/>3405</div>\n"""
                u"""<div class="extension contestador">"""
                u"""Recepcio<br/>3193</div>\n"""
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
        for time,hour in enumerate(parsedTimeIntervals[1:]):
            if now < hour:
                break
        return day,time+1

    def getYaml(self):
        return self.yaml


class HtmlGenFromYaml(HtmlGen):
    def __init__(self, yaml):
        self.yaml = yaml

    def comparePaused(self, other):
        def getPaused(yaml,day,time):
            if ("paused" 
                in yaml and
                day
                in yaml.paused and
                time
                in yaml.paused[day]):
                return set(
                    yaml.paused[day][time])
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
            for time in self.yaml.timetable[day]:
                selfPaused = getPaused(
                    self.yaml,day,time)
                otherPaused = getPaused(
                    other.yaml,day,time)
                removedInTurn = selfPaused - otherPaused
                addedInTurn = otherPaused - selfPaused
                for name in addedInTurn:
                    added.add((day,time,name))
                for name in removedInTurn:
                    removed.add((day,time,name))
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
            for time in self.yaml.timetable[day]:
                for name in self.yaml.colors.keys():
                    if (day,time,name) in added:
                       if day not in response:
                           response[day]=ns()
                       if time not in response[
                           day]:
                           response[day][time]=ns()
                       ext = self.nameToExtension(name)
                       response[day][time][ext]="added"
                    if (day,time,name) in removed:
                       if day not in response:
                           response[day]=ns()
                       if time not in response[
                           day]:
                           response[day][time]=ns()
                       ext = self.nameToExtension(name)
                       response[day][time][ext]="removed"

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


def solution2schedule(config, solution, date=None):
    nhours = len(config.hours)-1
    tt = ns(
        (day, [
            [None for i in xrange(config.nTelefons)]
            for j in xrange(nhours)
        ])
        for day in config.diesVisualitzacio
    )
    for day in config.diesVisualitzacio:
        for time in range(nhours):
            for tel in range(config.nTelefons):
                tt[day][time][tel]=solution.get(
                    (day,time,tel),
                    'festiu'
                ).lower()
    result=ns()
    result.week =str(HtmlGen.iniciSetmana(date))
    result.days = config.diesVisualitzacio
    result.hours = config.hours
    result.turns = ["T"+str(i+1) for i in range(config.nTelefons)]
    result.timetable = tt
    result.colors = config.colors
    result.extensions = config.extensions
    result.names = config.names
    return result

class HtmlGenFromSolution(HtmlGen):

    def __init__(self, config, solution, date=None):
        self.yaml = solution2schedule(config,solution,date)



def schedule2asterisk(schedule):
    r = []
    tt = schedule.timetable
    ext = schedule.extensions
    for d in tt.keys():
        for ti, t in enumerate(tt[d]):
            r+=[
                u'[entrada_cua_{}_{}]'.format(d,ti+1),
                u'music=default',
                u'strategy=linear',
                u'eventwhencalled=yes',
                u'timeout=15',
                u'retry=1',
                u'wrapuptime=0',
                u'maxlen = 0',
                u'; Periodic-announce = /var/lib/asterisk/sounds/bienvenida',
                u'Periodic-announce-frequency = 15',
                u'announce-frequency = 0',
                u'announce-holdtime = no',
                u'announce-position =no',
                u'context = bustia_veu',
            ] + [
                u"member = SIP/{},{}"
                    .format(ext[m],index+1)
                for index,m in enumerate(tt[d][ti])
            ]
    return u'\n'.join(r)+u'\n'

# vim: et
