# -*- coding: utf-8 -*-

from flask import (
    Flask, Response, request,
    redirect, url_for,
    send_from_directory,
    )
from datetime import datetime, timedelta
from yamlns import namespace as ns
from . import schedulestorage
from .pbxmockup import PbxMockup
from .htmlgen import HtmlGen
from .remote import remotewrite
import os

packagedir = os.path.join(os.path.dirname(__file__))
schedules_path = os.path.join(packagedir,'..','graelles')
schedules = schedulestorage.Storage(schedules_path)
staticpath = os.path.join(packagedir,'dist')


def pbx(alternative = None):
    if alternative:
        pbx.cache = alternative
    if not hasattr(pbx,'cache'):
        p = PbxMockup(now)
        p.reconfigure(schedules.load(thisweek()))
        pbx.cache = p
    return pbx.cache

def now():
    return datetime.now()

def anow():
    return datetime(2016,12,27,10,23,23)

def thisweek():
    return str(now().date() - timedelta(days=now().weekday()))

config=None

try:
    import config
except ImportError:
    pass

app = Flask(__name__)

def publishStatic(graella):
    if not config: return
    if not hasattr(config, 'publishStatic'): return
    params = config.publishStatic
    sched=HtmlGen(graella)
    remotewrite(
        params.user,
        params.host,
        os.path.join(params.path,
            'graella-{week}.html'.format(**graella)),
        sched.html(),
        )

class ApiError(Exception): pass

import decorator

@decorator.decorator
def yamlerrors(f,*args,**kwd):
    try:
        return f(*args,**kwd)
    except ApiError as e:
        raise
        return yamlfy(
            error=str(e),
            status=500,
            )

@app.route('/')
@app.route('/<file>')
def tomatic(file=None):
    return send_from_directory(staticpath, file or 'index.html')

@app.route('/api/graella-<week>.yaml')
@app.route('/api/graella/<week>')
def graellaYaml(week):
    # TODO: ensure week is an iso date
    # TODO: ensure week is monday

    schedule = schedules.load(week)

    return Response(
        schedule.dump(),
        mimetype = 'application/x-yaml',
        )

@app.route('/api/graella/<week>/<day>/<int:houri>/'
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
    publishStatic(graella)
    return graellaYaml(week)


@app.route('/api/graella/list')
def listGraelles():
    return Response(
        ns(weeks=schedules.list()).dump(),
        mimetype = 'application/x-yaml')

@app.route('/api/graella', methods=['POST'])
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
    publishStatic(graella)
    return yamlfy(result='ok')

@app.route('/api/queue')
def get_queue():
    return yamlfy(
        currentQueue = pbx().currentQueue()
    )

@app.route('/api/queue/add/<person>')
def add_line(person):
    p = pbx()
    p.addLine(person)
    return yamlfy(
        currentQueue = p.currentQueue()
    )

@app.route('/api/queue/pause/<person>')
def pause_line(person):
    p = pbx()
    p.pause(person)
    return yamlfy(
        currentQueue = p.currentQueue()
    )

@app.route('/api/queue/resume/<person>')
def resume_line(person):
    p = pbx()
    p.resume(person)
    return yamlfy(
        currentQueue = p.currentQueue()
    )

@app.route('/api/persons/')
def personInfo():
    config = ns.load('config.yaml')
    result = ns(
        names = config.names,
        extensions = config.extensions,
        tables = config.taules,
        colors = config.colors,
    )
    return yamlfy(persons=result)

@app.route('/api/person/<person>', methods=['POST'])
def setPersonInfo(person):
    config = ns.load('config.yaml')
    print(request.data)
    data = ns.loads(request.data)
    if 'name' in data:
        config.names[person] = data.name
    if 'extension' in data:
        config.extensions[person] = data.extension
    if 'table' in data:
        config.taules[person] = data.table
    if 'color' in data:
        config.colors[person] = data.color
    config.dump('config.yaml')
    result = ns(
        names = config.names,
        extensions = config.extensions,
        tables = config.taules,
        colors = config.colors,
    )
    return yamlfy(persons=result)


def yamlfy(status=200, data=[], **kwd):
    return Response(ns(
        data, **kwd
        ).dump(), status,
        mimetype = 'application/x-yaml',
    )

# vim: ts=4 sw=4 et
