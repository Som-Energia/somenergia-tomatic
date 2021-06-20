# -*- coding: utf-8 -*-

from fastapi import (
    FastAPI,
    Request,
    Form,
    WebSocket,
)
from fastapi.responses import (
    FileResponse,
    Response,
)

from datetime import datetime, timedelta, timezone
import urllib.parse
import decorator
import erppeek
from pathlib2 import Path
from yamlns import namespace as ns
from consolemsg import error, step, warn, u

from .callinfo import CallInfo
from .callregistry import CallRegistry
from . import schedulestorage
from .asteriskfake import AsteriskFake
from .pbxqueue import PbxQueue
from . import persons

try:
    import dbconfig
except ImportError:
    dbconfig = None


packagedir = Path(__file__).parent
distpath = packagedir/'dist'
staticpath = packagedir/'static'
schedules = schedulestorage.Storage.default()

def fillConfigurationInfo():
    return ns.load('config.yaml')
CONFIG = fillConfigurationInfo()


def erp():
    # TODO: Further checks, is the connection still alive?
    if hasattr(erp,'client'):
        return erp.client
    erp.client = erppeek.Client(**dbconfig.erppeek)
    return erp.client
erp() # Comment this out to connect the erp lazily


def pbx(alternative = None, queue=None):
    if alternative:
        pbx.cache = PbxQueue(alternative, queue)
    if not hasattr(pbx,'cache'):
        # A fake PBX loaded with the queue scheduled for now
        p = pbx(AsteriskFake(), 'somenergia')
        initialQueue = schedules.queueScheduledFor(now())
        p.setQueue(initialQueue)
    return pbx.cache

def now():
    return datetime.now()

def anow():
    return datetime(2020,11,9,10,23,23)

def thisweek():
    return format(now().date() - timedelta(days=now().weekday()))

from .planner_api import api as Planner
from fastapi.websockets import WebSocket

app = FastAPI()
#app.register_blueprint(Planner, url_prefix='/api/planner')


class ApiError(Exception): pass

def yamlfy(status=200, data=[], **kwd):
    output = ns(data, **kwd)
    return Response(output.dump(),
        status,
        media_type = 'application/x-yaml',
    )


@decorator.decorator
def yamlerrors(f,*args,**kwd):
    try:
        return f(*args,**kwd)
    except ApiError as e:
        error("ApiError: {}", e)
        return yamlfy(
            error=format(e),
            status=400,
            )
    except Exception as e:
        error("UnexpectedError: {}", e)
        return yamlfy(
            error=format(e),
            status=500,
            )


@app.get('/favicon.ico')
def favicon():
    return FileResponse(staticpath / 'favicon.ico')

@app.get('/')
@app.get('/{file}')
def tomatic(file=None):
    return FileResponse(distpath / (file or 'index.html'))

@app.get('/api/graella/list')
@yamlerrors
def listGraelles():
    step("runing listGraelles")
    return yamlfy(weeks=schedules.list())

@app.get('/api/graella-{week}.yaml')
@app.get('/api/graella/{week}')
@yamlerrors
def graellaYaml(week):
    schedule = schedules.load(week)

    return yamlfy(**schedule)

@app.patch('/api/graella/{week}/{day}/{houri}/{turni}/{name}')
@yamlerrors
async def editSlot(week, day, houri: int, turni: int, name, request: Request):
    user = await request.body().split('"')[1]
    graella = schedules.load(week)
    # TODO: Ensure day, houri, turni and name are in graella
    oldName = graella.timetable[day][int(houri)][int(turni)]
    graella.timetable[day][int(houri)][int(turni)] = name
    graella.overload = graella.get('overload', ns())
    graella.overload[oldName] = graella.overload.get(oldName, 0) -1
    graella.overload[name] = graella.overload.get(name, 0) +1
    logmsg = (
        "{}: {} ha canviat {} {}-{} {} de {} a {}".format(
        datetime.now(),
        user, # TODO: ERP user
        day,
        graella.hours[int(houri)],
        graella.hours[int(houri)+1],
        graella.turns[int(turni)],
        oldName,
        name
        ))
    print(logmsg)
    graella.setdefault('log',[]).append(logmsg)
    schedules.save(graella)
    schedulestorage.publishStatic(graella)
    return graellaYaml(week)


@app.post('/api/graella')
@yamlerrors
def uploadGraella(week=None):
    step("uploading {}".format(request.files))
    if 'yaml' not in request.files:
        error("Cap graella pujada")
        return "KO"
    yaml = request.files['yaml']
    if yaml.content_length > 30:
        warn("Pujat yaml sospitosament llarg: {} bytes"
            .format(yaml.content_length))
        return "KO"
    graella = ns.load(yaml.stream)
    logmsg = (
        "{}: {} ha pujat {} ".format(
        datetime.now(),
        "nobody", # TODO: ERP user
        graella.week,
        ))
    graella.setdefault('log',[]).append(logmsg)
    schedules.save(graella)
    schedulestorage.publishStatic(graella)
    return yamlfy(result='ok')

@app.get('/api/graella/retireold')
@yamlerrors
def retireOldTimeTable():
    today = datetime.today()
    twoMondaysAgo = str((today - timedelta(days=today.weekday()+7*2)).date())
    step("Retiring timetables older than {}", twoMondaysAgo)
    try:
        schedules.load(twoMondaysAgo)
    except:
        raise ApiError("Graella {} no trobada, potser ja ha estat retirada".format(twoMondaysAgo))
    else:
        schedules.retireOld(twoMondaysAgo)
    return yamlfy(result='ok')


def cachedQueueStatus(force=False):
    now = datetime.now()
    if not force and hasattr(cachedQueueStatus, 'value') and cachedQueueStatus.timestamp > now:
        return cachedQueueStatus.value
    cachedQueueStatus.timestamp = now + timedelta(seconds=5)
    cachedQueueStatus.value = pbx().queue()
    return cachedQueueStatus.value

@app.get('/api/queue')
@yamlerrors
def get_queue():
    return yamlfy(
        currentQueue = cachedQueueStatus()
    )

@app.get('/api/queue/add/{person}')
@yamlerrors
def add_line(person):
    p = pbx()
    p.add(person)
    return yamlfy(
        currentQueue = cachedQueueStatus(force=True)
    )

@app.get('/api/queue/pause/{person}')
@yamlerrors
def pause_line(person):
    p = pbx()
    p.pause(person)
    return yamlfy(
        currentQueue = cachedQueueStatus(force=True)
    )

@app.get('/api/queue/resume/{person}')
@yamlerrors
def resume_line(person):
    p = pbx()
    p.resume(person)
    return yamlfy(
        currentQueue = cachedQueueStatus(force=True)
    )

@app.get('/api/persons/extension/{extension}')
@yamlerrors
def personInfoFromExtension(extension):
    allpersons=persons.persons()
    names = [name for name,ext in allpersons.extensions.items() if ext == extension]
    if not names:
        return 'nobody@somenergia.coop'
    name = names[0]
    email = allpersons.emails[name]
    return email

@app.get('/api/persons/')
@yamlerrors
def personInfo():
    result=persons.persons()
    return yamlfy(persons=result)

@app.post('/api/person/{person}')
@yamlerrors
async def setPersonInfo(person, request: Request):
    data = ns.loads(await request.body())
    persons.update(person, data)
    return yamlfy(persons=persons.persons())

@app.get('/api/busy/{person}')
@yamlerrors
def busy(person):
    from . import busy
    return yamlfy(**busy.busy(person))

@app.post('/api/busy/{person}')
@yamlerrors
async def busy_post(person, request: Request):
    from . import busy
    data = ns.loads(await request.body())
    return yamlfy(**busy.update_busy(person, data))

@app.get('/api/busy/download/weekly')
@yamlerrors
def downloadWeeklyBusy():
    response = FileResponse(
        path='../indisponibilitats.conf',
        as_attachment=True,
        media_type='text/plain',
    )
    print("response {}".format(response))
    return response

@app.get('/api/busy/download/oneshot')
@yamlerrors
def downloadOneShotBusy():
    return FileResponse(
        '../oneshot.conf',
        as_attachment=True,
        media_type='text/plain',
    )

@app.get('/api/shifts/download/credit/{week}')
@yamlerrors
def downloadWeekShiftCredit(week):
    try:
        credit = schedules.credit(week)
    except schedulestorage.StorageError as e:
        raise ApiError(e)
    return yamlfy(**credit)

@app.get('/api/shifts/download/shiftload/{week}')
def downloadShiftLoad(week):
    loadfile = Path('carrega-{}.csv'.format(week))

    return FileResponse(
        str('..'/loadfile),
        as_attachment=True,
        media_type='text/csv',
    )

@app.get('/api/shifts/download/overload/{week}')
def downloadOverload(week):
    loadfile = Path('overload-{}.yaml'.format(week))

    return FileResponse(
        str('..'/loadfile),
        as_attachment=True,
        media_type = 'application/x-yaml',
    )

def yamlinfoerror(code, message, *args, **kwds):
    error(message, *args, **kwds)
    return yamlfy(info=ns(
        info='',
        message=code,
    ))

@app.get('/api/info/{field}/{value}')
def getInfoPersonBy(field, value):
    decoded_field = urllib.parse.unquote(value)
    info = CallInfo(erp())
    data = None
    try:
        data = info.getByField(field, decoded_field, shallow=True)
        if data is None:
            return 404
    except ValueError:
        return yamlinfoerror('error_getBy'+field.title(),
            "Getting information searching {}='{}'.", field, value)

    message = 'ok'
    if not data.partners:
        message = 'no_info'
    elif data.partners == "Masses resultats":
        message = 'response_too_long'

    result = ns(
        info=data,
        message=message,
    )
    return yamlfy(info=result)

@app.post('/api/info/contractdetails')
async def getContractDetails(request: Request):
    params = ns.loads(await request.body())
    info = CallInfo(erp())
    data = info.contractDetails(params.contracts)
    result = ns(
        info=data,
        message='ok',
    )
    return yamlfy(info=result)


@app.post('/api/info/ringring')
def callingPhone(phone: str = Form(...), ext: str = Form(...)):
    time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    CallRegistry().updateCall(ext, fields=ns(
        data = time,
        telefon = phone,
        motius = "",
        partner = "",
        contracte = "",
    ))
    nNotified = 0
    if hasattr(app, "sessionBackChannel"):
        nNotified = app.sessionBackChannel.say_incoming_call(ext, phone, time)
    result = ns(
        notified=nNotified,
        phone=phone,
        ext=ext,
    )
    return yamlfy(info=result)


@app.get('/api/socketInfo')
def getConnectionInfo():
    result = ns(
        port_ws=CONFIG.websocket_port,
        message="ok"
    )
    return yamlfy(info=result)


@app.get('/api/personlog/{extension}')
def getCallLog(extension):
    calls = CallRegistry().callsByExtension(extension)
    return yamlfy(
        info=ns(
            info=calls,
            message='ok',
        )
    )

@app.post('/api/updatelog/{extension}')
async def updateCallLog(extension, request: Request):
    body = await request.body()
    fields = ns.loads(body)
    CallRegistry().updateCall(extension, fields=fields)
    if hasattr(app, "sessionBackChannel"):
        app.sessionBackChannel.say_logcalls_has_changed(extension)
    return yamlfy(info=ns(message='ok'))


@app.get('/api/updateClaims')
def updateClaimTypes():
    message = 'ok'

    CallRegistry().importClaimTypes(erp())
    return yamlfy(info=ns(message='ok'))

@app.get('/api/getClaims')
def getClaimTypes():
    message = 'ok'
    claims = CallRegistry().claimTypes()
    if not claims:
        error("File of claims does not exist")
        return yamlfy(info=ns(
            message="error",
            claims=[],
            dict={},
        ))
    claims_dict = CallRegistry().claimKeywords()
    if not claims_dict:
        error("File of claims dict does not exist")
        return yamlfy(info=ns(
            message="error",
            claims=[],
            dict={},
        ))

    result = ns(
        message=message,
        claims=claims,
        dict=claims_dict,
    )
    return yamlfy(info=result)


@app.post('/api/atrCase')
async def postAtrCase(request: Request):

    atc_info = ns.loads(await request.body())
    CallRegistry().annotateClaim(atc_info)
    return yamlfy(info=ns(
        message="ok"
    ))


@app.get('/api/getInfos')
def getInfos():
    infos = CallRegistry().infoRequestTypes()
    if not infos:
        return yamlinfoerror("error",
            "Unable to info request types")
    return yamlfy(info = ns(
        message='ok',
        infos=infos,
    ))


@app.post('/api/infoCase')
async def postInfoCase(request: Request):
    info = ns.loads(await request.body())
    CallRegistry().annotateInfoRequest(info)
    return yamlfy(info=ns(
        message="ok"
    ))



# vim: ts=4 sw=4 et
