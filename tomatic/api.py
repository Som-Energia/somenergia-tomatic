# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from flask import (
    Flask, Response, request,
    send_from_directory,
    send_file,
    )
from datetime import datetime, timedelta
from yamlns import namespace as ns
from consolemsg import error, step, warn
from .callinfo import CallInfo
from websocket_server import WebsocketServer
from . import schedulestorage
from .pbxmockup import PbxMockup
from .htmlgen import HtmlGen
from .remote import remotewrite
import os
import erppeek
from sheetfetcher import SheetFetcher
from threading import Semaphore, Thread
import urllib

try:
    import dbconfig
except ImportError:
    dbconfig = None

packagedir = os.path.join(os.path.dirname(__file__))
schedules_path = os.path.join(packagedir,'..','graelles')
schedules = schedulestorage.Storage(schedules_path)
staticpath = os.path.join(packagedir,'dist')
websockets = {}


def fillConfigurationInfo():
    return ns.load('config.yaml')


CONFIG = fillConfigurationInfo()


SHEETS = {
    "infos_log": 0,
    "claims_log": 4,
    "general_reasons": 2,
    "specific_reasons": 3
}

LOGS = {
    "date": 0,
    "person": 1,
    "phone": 2,
    "partner": 3,
    "contract": 4,
    "reason": 5,
    "proc": 6,
    "improc": 7,
    "extras": 8,
}


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

dbconfig=None

try:
    import dbconfig
except ImportError:
    pass

app = Flask(__name__)
app.wserver = None
app.drive_semaphore = Semaphore()

def publishStatic(graella):
    if not dbconfig: return
    if not hasattr(dbconfig, 'tomatic'): return
    if not hasattr(dbconfig.tomatic, 'publishStatic'): return
    params = dbconfig.tomatic.publishStatic
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
        error("ApiError: {}", e)
        raise
        return yamlfy(
            error=str(e),
            status=500,
            )
    except Exception as e:
        error("UnexpectedError: {}", e)
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
    myname = request.data.split('"')[1]
    # TODO: Same ensures than graella
    graella = schedules.load(week)
    # TODO: Ensure day, houri, turni and name are in graella
    oldName = graella.timetable[day][int(houri)][int(turni)]
    graella.timetable[day][int(houri)][int(turni)] = name
    logmsg = (
        "{}: {} ha canviat {} {}-{} {} de {} a {}".format(
        datetime.now(),
        myname, # TODO: ERP user
        day,
        graella.hours[int(houri)], 
        graella.hours[int(houri)+1], 
        graella.turns[int(turni)],
        oldName,
        name
        ))
    graella.setdefault('log',[])
    print(logmsg)
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
    print("uploading", request.files)
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
    print(logmsg)
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
        notoi_id = config.notoi_ids
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
    if 'notoi_id' in data:
        config.notoi_ids[person] = data.notoi_id
    config.dump('config.yaml')
    result = ns(
        names = config.names,
        extensions = config.extensions,
        tables = config.taules,
        colors = config.colors,
        notoi_id = config.notoi_ids
    )
    return yamlfy(persons=result)

@app.route('/api/busy/<person>', methods=['GET'])
def busy(person):
    from . import busy
    return yamlfy(**busy.busy(person))

@app.route('/api/busy/<person>', methods=['POST'])
def busy_post(person):
    from . import busy
    data = ns.loads(request.data)
    return yamlfy(**busy.update_busy(person, data))


@app.route('/api/info/phone/<phone>', methods=['GET'])
@yamlerrors
def getInfoPersonByPhone(phone):
    message = 'ok'
    o = erppeek.Client(**dbconfig.erppeek)
    info = CallInfo(o)
    data = None
    try:
        data = info.getByPhone(phone)
        if (not data.partners):
            message = 'no_info'
        elif data.partners == "Masses resultats":
            message = 'response_too_long'
    except ValueError:
        message = 'error_getByPhone'
        error("Getting information from {}.", phone)
    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/info/name/<name>', methods=['GET'])
def getInfoPersonByName(name):
    decoded_name = urllib.unquote(name)
    message = 'ok'
    o = erppeek.Client(**dbconfig.erppeek)
    info = CallInfo(o)
    data = None
    try:
        data = info.getByName(decoded_name)
        if (not data.partners):
            message = 'no_info'
        elif (data.partners == "Masses resultats"):
            message = 'response_too_long'
    except ValueError:
        message = 'error_getByName'
        error("Getting information from {}.", name)
    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/info/nif/<nif>', methods=['GET'])
def getInfoPersonByNif(nif):
    message = 'ok'
    o = erppeek.Client(**dbconfig.erppeek)
    info = CallInfo(o)
    data = None
    try:
        data = info.getByDni(nif)
        if (not data.partners):
            message = 'no_info'
        elif (data.partners == "Masses resultats"):
            message = 'response_too_long'
    except ValueError:
        message = 'error_getByDni'
        error("Getting information from {}.", nif)
    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/info/soci/<iden>', methods=['GET'])
def getInfoPersonBySoci(iden):
    message = 'ok'
    o = erppeek.Client(**dbconfig.erppeek)
    info = CallInfo(o)
    data = None
    try:
        data = info.getBySoci(iden)
        if (not data.partners):
            message = 'no_info'
        elif (data.partners == "Masses resultats"):
            message = 'response_too_long'
    except ValueError:
        message = 'error_getBySoci'
        error("Getting information from {}.", iden)
    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/info/email/<email>', methods=['GET'])
def getInfoPersonByEmail(email):
    message = 'ok'
    o = erppeek.Client(**dbconfig.erppeek)
    info = CallInfo(o)
    data = None
    try:
        data = info.getByEmail(email)
        if (not data.partners):
            message = 'no_info'
        elif (data.partners == "Masses resultats"):
            message = 'response_too_long'
    except ValueError:
        message = 'error_getByEmail'
        error("Getting information from {}.", email)
    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/info/all/<field>', methods=['GET'])
def getInfoPersonBy(field):
    decoded_field = urllib.unquote(field)
    message = 'ok'
    o = erppeek.Client(**dbconfig.erppeek)
    info = CallInfo(o)
    data = None
    try:
        data = info.getByData(decoded_field)
        if (not data.partners):
            message = 'no_info'
        elif (data.partners == "Masses resultats"):
            message = 'response_too_long'
    except ValueError:
        message = 'error_getByData'
        error("Getting information from {}.", field)
    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/info/ringring', methods=['POST'])
def callingPhone():
    data = request.form.to_dict()
    phone = data['phone']
    ext = data['ext']
    clients = websockets.get(ext, [])
    time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    try:
        logs = ns.load(CONFIG.my_calls_log)
        if ext not in logs:
            logs[ext] = []
        elif len(logs[ext]) == 20:
            logs[ext].pop(0)
        info = {
            "data": time,
            "telefon": phone,
            "motius": "",
            "partner": "",
            "contracte": "",
        }
        logs[ext].append(info)
        logs.dump(CONFIG.my_calls_log)
    except ValueError:
        error("[S] Opening file {} but it doesn't exists", CONFIG.my_calls_log)

    if not clients:
        error("Calling {} but has no client.", ext)
    for client in clients:
        app.wserver.send_message(client, "PHONE:" + phone + ":" + time)
    result = ns(
        notified=len(clients),
        phone=phone,
        ext=ext,
    )
    return yamlfy(info=result)


@app.route('/api/socketInfo', methods=['GET'])
def getConnectionInfo():
    result = ns(
        ip=CONFIG.websocket_ip,
        port_ws=CONFIG.websocket_port,
        message="ok"
    )
    return yamlfy(info=result)


def initialize_client(client, server, extension):
    client_left(client, server)
    step("Identifying client as {}", extension)
    if extension not in websockets:
        websockets[extension] = []
    websockets[extension].append(client)


def say_new_user_logged(client, server, extension, iden):
    step("Saying to the page that now {} is there", iden)
    clients = websockets.get(extension, [])
    if not clients:
        error("Trying to send message to {} but has no client.", extension)
    for client in clients:
        app.wserver.send_message(client, "IDEN:" + iden)


def say_logcalls_has_changed(extension):
    clients = websockets.get(extension, [])
    if not clients:
        error("Trying to send message to {} but has no client.", extension)
    for client in clients:
        app.wserver.send_message(client, "REFRESH:" + extension)


def on_message_recieved(client, server, message):
    divided_message = message.split(":")
    type_of_message = divided_message[0]
    if type_of_message == "IDEN":
        extension = divided_message[1]
        iden = divided_message[2]
        initialize_client(client, server, extension)
        say_new_user_logged(client, server, extension, iden)
    else:
        error("Type of message not recognized.")


def client_left(client, server):
    for extension in websockets:
        if client in websockets[extension]:
            step("Unidentifying client as {}", extension)
            websockets[extension].remove(client)
            break
    else:
        warn("New client")


def startCallInfoWS(app):
    app.wserver = WebsocketServer(
        CONFIG.websocket_port,
        host=CONFIG.websocket_ip
    )
    app.wserver.set_fn_message_received(on_message_recieved)
    app.wserver.set_fn_client_left(client_left)
    thread = Thread(target=app.wserver.run_forever)
    thread.start()
    return thread


@app.route('/api/callReasons/<info_type>', methods=['GET'])
def getReasonsInfo(info_type):
    message = 'ok'
    try:
        fetcher = SheetFetcher(
            documentName=CONFIG.call_reasons_document,
            credentialFilename=CONFIG.credential_name,
        )
        reasons = fetcher.get_fullsheet(
                SHEETS["general_reasons"] if info_type == 'general' else SHEETS["specific_reasons"]
        )
    except IOError:
        reasons = []
        message = 'error_get_fullsheet'
        error("Trying to open {} drive sheet.", CONFIG.call_reasons_document)
    result = ns(
        info=reasons,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/infoReasons', methods=['POST'])
def savePhoneInfosLog():
    message = 'ok'
    try:
        info = ns.loads(request.data)
        fetcher = SheetFetcher(
            documentName=CONFIG.call_reasons_document,
            credentialFilename=CONFIG.credential_name,
        )
        row = [
            info.date,
            info.person,
            info.phone,
            info.reason,
            info.extra,
        ]
        with app.drive_semaphore:
            fetcher.add_to_last_row(SHEETS["infos_log"], row)
    except IOError:
        error("Saving {} to the drive sheet.", CONFIG.call_reasons_document)
        message = 'error_add_to_las_row'
    result = ns(
        message=message
    )
    return yamlfy(info=result)


@app.route('/api/claimReasons', methods=['POST'])
def savePhoneClaimsLog():
    message = 'ok'
    try:
        info = ns.loads(request.data)
        fetcher = SheetFetcher(
            documentName=CONFIG.call_reasons_document,
            credentialFilename=CONFIG.credential_name,
        )
        row = [
            info.date,
            info.person,
            info.partner,
            info.contract,
            info.cups,
            info.user,
            info.reason,
            info.procedente,
            info.improcedente,
            info.solved,
            info.observations,
        ]
        with app.drive_semaphore:
            fetcher.add_to_last_row(SHEETS["claims_log"], row)
    except IOError:
        error("Saving {} to the drive sheet.", CONFIG.call_reasons_document)
        message = 'error_add_to_las_row'
    result = ns(
        message=message
    )
    return yamlfy(info=result)


@app.route('/api/log/<phone>', methods=['GET'])
def getPhoneLog(phone):
    message = 'ok'
    try:
        fetcher = SheetFetcher(
            documentName=CONFIG.call_reasons_document,
            credentialFilename=CONFIG.credential_name,
        )
        log = fetcher.get_fullsheet(SHEETS["infos_log"])
    except IOError:
        log = []
        message = 'error_get_fullsheet'
        error("Getting reason calls from {}.", CONFIG.call_reasons_document)
    reasons = filter(lambda x: x[LOGS["phone"]] == phone, log)
    reasons.sort(key=lambda x: datetime.strptime(x[0], '%d-%m-%Y %H:%M:%S'))
    result = ns(
        info=reasons,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/personlog/<ext>', methods=['GET'])
def getMyLog(ext):
    message = 'ok'
    mylog = ""
    try:
        logs = ns.load(CONFIG.my_calls_log)
        if ext in logs:
            mylog = logs[ext]
        else:
            message = 'not_registers_yet'
            error("{} does not appear in the register.", ext)
    except IOError:
        f = open(CONFIG.my_calls_log, "w+")
        f.write("nom:\r\n")
        f.write("- data: DD-MM-YYYY HH:MM:SS\r\n")
        f.write("  telefon: \'Num de Telefon\' \r\n")
        f.write("  partner: NumPartner\r\n")
        f.write("  contracte: \'Num de Contracte\' \r\n")
        f.write("  motius: \'[ETIQUETA] Motiu1, [ETIQUETA] Motiu2\' \r\n")
        f.close()
    result = ns(
        info=mylog,
        message=message,
    )
    return yamlfy(info=result)


@app.route('/api/updatelog/<ext>', methods=['POST'])
def updateMyLog(ext):
    msg = 'ok'
    try:
        logs = ns.load(CONFIG.my_calls_log)
        info = ns.loads(request.data)
        for call in logs[ext]:
            if call.data == info.data:
                i = logs[ext].index(call)
                logs[ext].pop(i)
                logs[ext].insert(i, info)
                break
        logs.dump(CONFIG.my_calls_log)
        say_logcalls_has_changed(ext)
    except ValueError:
        msg = 'error_update_log'
        error("[U] Opening file {} but it doesn't exists", CONFIG.my_calls_log)
    result = ns(
        message=msg
    )
    return yamlfy(info=result)

@app.route('/api/busy/download/weekly')
def downloadWeeklyBusy():
    print("joder")
    response = send_file(
        '../indisponibilitats.conf',
        as_attachment=True,
        mimetype='text/plain',
    )
    print("response {}".format(response))
    return response

@app.route('/api/busy/download/oneshot')
def downloadOneShotBusy():
    return send_file(
        '../oneshot.conf',
        as_attachment=True,
        mimetype='text/plain',
    )

def yamlfy(status=200, data=[], **kwd):
    return Response(ns(
        data, **kwd
        ).dump(), status,
        mimetype = 'application/x-yaml',
    )


# vim: ts=4 sw=4 et
