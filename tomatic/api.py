# -*- coding: utf-8 -*-

from flask import (
    Flask, Response, request,
    redirect, url_for,
    )
from htmlgen import HtmlGenFromYaml, HtmlGenFromAsterisk
from datetime import datetime
from yamlns import namespace as ns
from . import schedulestorage

hs = {}

schedules = schedulestorage.Storage('graelles')


def pbx(alternative = None):
    if alternative:
        pbx.cache = alternative
    if not hasattr(pbx,'cache'):
        pbx.cache = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
    return pbx.cache

config=None
try:
    import config
except ImportError:
    pass
if config or True:
    import asterisk
    from paramiko import SSHClient,AutoAddPolicy
    from Asterisk.Manager import Manager
app = Flask(__name__)
startOfWeek = HtmlGenFromYaml.iniciSetmana(
    datetime.now()
)
def loadYaml(yaml):
    global hs
    parsedYaml = ns.loads(yaml)
    week = str(parsedYaml.setmana)
    setmana_underscore = week.replace("-","_")
    hs[setmana_underscore]=HtmlGenFromYaml(parsedYaml)

def loadAsterisk(yaml,date=None):
    global hs
    hs[startOfWeek.strftime("%Y_%m_%d")
        ]=HtmlGenFromAsterisk(
            yaml,pbx().receiveConf()
        )

def setNow(year,month,day,hour,minute):
    global now
    now=datetime(year,month,day,hour,minute)

def trustedStaticFile(path):
    with open(path) as f:
        return f.read()

staticpath = 'tomatic/static'

@app.route('/')
def tomatic():
    return trustedStaticFile(staticpath+'/tomatic.html')

@app.route('/graella.js')
def graella_js():
    return trustedStaticFile(staticpath+'/graella.js')

@app.route('/graella-<week>.yaml')
@app.route('/graella/<week>')
def graellaYaml(week):
    # TODO: ensure week is an iso date
    # TODO: ensure week is monday

    schedule = schedules.load(week)

    return Response(
        schedule.dump(),
        mimetype = 'application/x-yaml',
        )

@app.route('/graella/<week>/<day>/<int:houri>/'
        '<int:turni>/<name>', methods=['UPDATE'])
def editSlot(week, day, houri, turni, name):
    # TODO: Same ensures than graella
    graella = schedules.load(week)
    # TODO: Ensure day, houri, turni and name are in graella
    oldName = graella.timetable[day][int(houri)][int(turni)]
    graella.timetable[day][int(houri)][int(turni)] = name
    logmsg = (
        "{}: {} ha canviat {} {}-{} {} de {} a {}".format(
        datetime.now(),
        "nobody", # TODO: ERP user
        day,
        graella.hours[int(houri)], 
        graella.hours[int(houri)+1], 
        graella.turns[int(turni)],
        oldName,
        name
        ))
    graella.setdefault('log',[])
    print logmsg
    graella.log.append(logmsg)
    schedules.save(graella)
    return graellaYaml(week)


@app.route('/graella/list')
def listGraelles():
    return Response(
        ns(weeks=schedules.list()).dump(),
        mimetype = 'application/x-yaml')

@app.route('/graella', methods=['POST'])
def uploadGraella(week=None):
    print "uploading", request.files
    if 'yaml' not in request.files:
        print("Cap graella pujada")
        return "KO"
    yaml = request.files['yaml']
    if yaml.content_length > 30:
        print("Pujat yaml sospitosament llarg: {} bytes"
            .format(yaml.content_length))
        return "KO"
    graella = ns.load(yaml.stream)
    logmsg = (
        "{}: {} ha pujat {} ".format(
        datetime.now(),
        "nobody", # TODO: ERP user
        graella.date,
        ))
    graella.setdefault('log',[])
    print logmsg
    schedules.save(graella)
    return redirect(url_for('tomatic'))


@app.route('/boo')
def index():
    global now
    if not now:
        now=datetime.now()
    return get_queue(
        "_".join([
            str(now.year),
            "%02d" % now.month,
            "%02d" % now.day]),
        now.hour,
        now.minute
    )

@app.route('/getqueue/<setmana>/<hour>/<minute>')
def get_queue(setmana,hour,minute):
    loadAsterisk(yaml)
    year,month,day=(
        int(tok)
        for tok
        in setmana.split('_')
    )
    startOfWeek = HtmlGenFromYaml.iniciSetmana(
        datetime(year,month,day)
    )
    h = hs[startOfWeek.strftime("%Y_%m_%d")]
    day,turn = h.getCurrentQueue(
        datetime(year,month,day,int(hour),int(minute))
    )
    response = (h.htmlHeader()+
        h.htmlColors()+
        h.htmlSubHeader()+
        h.htmlSetmana()+
        h.partialCurrentQueue(day,turn)+
        h.htmlExtensions()+
        h.htmlFixExtensions()+
        h.htmlFooter()
    )
    return response


now = None
yaml = ns.load("templateTimetable.yaml")
yaml.setmana = startOfWeek.strftime("%Y-%m-%d")

# vim: ts=4 sw=4 et
