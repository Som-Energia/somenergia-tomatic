import random
import datetime
from yamlns import namespace as ns
from .scheduling import weekstart, nextweek, Scheduling

class HtmlGen(object):

    def __init__(self, yaml):
        self.yaml = yaml

    @staticmethod
    def iniciSetmana(date=None):
        if date is None:
            return nextweek(datetime.date.today())
        # take the monday of the week including that date
        return weekstart(date)

    def properName(self,name):
        sched = Scheduling(self.yaml)
        return sched.properName(name)

    def intervals(self):
        sched = Scheduling(self.yaml)
        return sched.intervals()

    def partialCoreTable(self,day,itime):
        return "".join([
            u"""<td class='{name}'>{properName}</td>\n"""
            .format(
                name=name,
                properName=self.properName(name)
            )
            for name in self.yaml.timetable[day][itime]
            ])

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
                    self.partialCoreTable(day,iturn)
                    for day in self.yaml.timetable.keys()
                    )
                for iturn,period in enumerate(self.intervals()
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

        def contrast(color):
            if len(color) == 3:
                color = ''.join(c+c for c in color)
            intensity = sum(int(h+l,16) for h,l in zip(color[0::2], color[1::2]))
            return "000000" if intensity > 300 else "FFFFFF"

        colors= "\n".join(
            ".{:<8} {{ background-color: #{}; color: #{}; }}".format(nom, color, contrast(color))
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

    def html(self):
        return (self.htmlHeader()+
            self.htmlColors()+
            self.htmlSubHeader()+
            self.htmlSetmana()+
            self.htmlTable()+
            self.htmlPenalties()+
            self.htmlExtensions()+
            self.htmlFooter()
        )

    # TODO deprecated
    def htmlPenalizations(self,minimumCost,penalties):
        return  '\n'.join([
            "",
            "<p>Penalitzacio: {}</p>".format(minimumCost),
            "<ul>",
            "\n".join(
                u"<li>{}: {}</li>".format(*reason)
                for reason in penalties
            ),
            "</ul>",
            '',
        ])

    def htmlPenalties(self):
        if 'cost' not in self.yaml and 'penalties' not in self.yaml:
            return (
                u"""<h3>Penalitzacions</h3>\n"""
                u"""<p>Sense penalitzacions</p>\n"""
            )

        if 'penalties' not in self.yaml:
            return (
                u"""<h3>Penalitzacions</h3>\n"""
                u"""<p>Penalitzacio: {}</p>\n""".format(self.yaml.cost)
            )

        html = "<h3>Penalitzacions</h3>\n"

        if 'cost' in self.yaml:
            html += "<p>Penalitzacio: {}</p>\n".format(self.yaml.cost)

        html += '\n'.join([
            "<ul>",
            "\n".join(
                u"<li>{}: {}</li>".format(*reason)
                for reason in self.yaml.penalties
            ),
            "</ul>",
            '',
        ])

        return html

    def nameToExtension(self, name):
        return self.yaml.extensions[name]

    def extensionToName(self, extension):
        extensions_inv = {
            extension : name
            for name, extension in self.yaml.extensions.items()
            }
        return extensions_inv[extension]

    def getYaml(self):
        return self.yaml

    @classmethod
    def fromSolution(cls, config, solution, date=None):
        from .scheduling import solution2schedule
        data = solution2schedule(config,solution,date)
        return cls(data)



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
