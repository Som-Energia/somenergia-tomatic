# -*- coding: utf-8 -*-

from flask import (
    Flask, Response, request,
    redirect, url_for,
    )
from datetime import datetime, timedelta
from yamlns import namespace as ns
from . import schedulestorage
from .pbxmockup import PbxMockup

hs = {}

schedules = schedulestorage.Storage('graelles')


def pbx(alternative = None):
    if alternative:
        pbx.cache = alternative
    if not hasattr(pbx,'cache'):
        pbx.cache = asterisk.Pbx(config.pbx)
    return pbx.cache

def now():
    return datetime.now()

def anow():
    return datetime(2016,12,27,10,23,23)

def thisweek():
    return str(now().date() - timedelta(days=now().weekday()))

p = PbxMockup(now)
#p.reconfigure(schedules.load(thisweek()))
pbx(p)

staticpath = 'tomatic/static'
config=None

try:
    import config
except ImportError:
    pass

if config or True:
    import asterisk

app = Flask(__name__)

def trustedStaticFile(path):
    with open(path) as f:
        return f.read()

from functools import wraps

def yamlerrors(f):
    @wraps(f)
    def error_hanlder(*args,**kwd):
        try:
            return f(*args,**kwd)
        except Exception as e:
            return yamlfy(
                error=str(e),
                status=500,
                )
    return error_hanlder

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
@yamlerrors
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
@yamlerrors
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
        graella.week,
        ))
    graella.setdefault('log',[])
    print logmsg
    schedules.save(graella)
    return yamlfy(result='ok')

@app.route('/queue')
def get_queue():
    return yamlfy(
        currentQueue = pbx().currentQueue()
    )

@app.route('/queue/add/<person>')
def add_to_queue(person):
    p = pbx()
    p.addLine(person)
    return yamlfy(
        currentQueue = p.currentQueue()
    )

@app.route('/queue/pause/<person>')
def pause_line(person):
    p = pbx()
    p.pause(person)
    return yamlfy(
        currentQueue = p.currentQueue()
    )

@app.route('/queue/resume/<person>')
def resume_line(person):
    p = pbx()
    p.resume(person)
    return yamlfy(
        currentQueue = p.currentQueue()
    )

def yamlfy(status=200, data=[], **kwd):
    return Response(ns(
        data, **kwd
        ).dump(), status,
        mimetype = 'application/x-yaml',
    )

# vim: ts=4 sw=4 et
