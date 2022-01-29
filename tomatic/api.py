# -*- coding: utf-8 -*-

from fastapi import (
    FastAPI,
    Request,
    Form,
    WebSocket,
    WebSocketDisconnect,
    File,
    UploadFile,
    Depends,
)
from fastapi.responses import (
    FileResponse,
    Response,
    RedirectResponse,
)
from starlette.middleware.sessions import SessionMiddleware
import asyncio
import re
import os
from datetime import datetime, timedelta, timezone
import urllib.parse
import decorator
import erppeek
from pathlib import Path
from yamlns import namespace as ns
from consolemsg import error, step, warn, u

from . import __version__ as version
from .callinfo import CallInfo
from .callregistry import CallRegistry
from . import schedulestorage
from .pbx import pbxqueue as pbx
from . import persons
from .backchannel import BackChannel

try:
    import dbconfig
except ImportError:
    dbconfig = None


packagedir = Path(__file__).parent
distpath = packagedir/'dist'
schedules = schedulestorage.Storage()

def fillConfigurationInfo():
    return ns.load('config.yaml')
CONFIG = fillConfigurationInfo()

from contextlib import contextmanager
@contextmanager
def erp():
    if not hasattr(erp,'clients'):
        erp.clients = []
        erp.available = []
    if not erp.available:
        newclient = erppeek.Client(**dbconfig.erppeek)
        erp.clients.append(newclient)
        erp.available.append(newclient)
    client = erp.available.pop()
    try:
        yield client
    finally:
        erp.available.append(client)

def now():
    return datetime.now()

def anow():
    return datetime(2020,11,9,10,23,23)

def thisweek():
    return format(now().date() - timedelta(days=now().weekday()))

from .planner_api import api as Planner
from .auth import router as Auth, validatedUser
from fastapi.websockets import WebSocket

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="Hola, Supers!")
app.include_router(Planner, prefix='/api/planner')
app.include_router(Auth, prefix='/api/auth')


def occurrencesInTurn(graella, day, houri, name):
    nominated = graella.timetable[day][int(houri)]
    return nominated.count(name)


class ApiError(Exception): pass

def yamlfy(status=200, data=[], **kwd):
    output = ns(data, **kwd)
    return Response(output.dump(),
        status,
        media_type = 'application/x-yaml',
    )

@decorator.decorator
async def ayamlerrors(f,*args,**kwd):
    try:
        return await f(*args,**kwd)
    except ApiError as e:
        error("ApiError: {}", e)
        return yamlfy(
            error=format(e),
            status=400,
            )
    except Exception as e:
        error("UnexpectedError: {}", e)
        import traceback
        error(''.join(traceback.format_exc()))
        return yamlfy(
            error=format(e),
            status=500,
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
        import traceback
        error(''.join(traceback.format_exc()))
        return yamlfy(
            error=format(e),
            status=500,
            )

backchannel = BackChannel()

@app.websocket('/backchannel')
async def websocketSession(websocket: WebSocket):
    await websocket.accept()
    session_id = str(websocket.client)
    def sender(message):
        step("WS {} send: {}", session_id, message)
        return websocket.send_text(message)

    backchannel.addSession(session_id, websocket, sender)
    try:
        while True:
            data = await websocket.receive_text()
            backchannel.receiveMessage(session_id, data)
    except WebSocketDisconnect:
        backchannel.onDisconnect(session_id)

@app.get('/')
@app.get('/{file}')
def tomatic(request: Request, file=None):
    return FileResponse(distpath / (file or 'index.html'))

@app.get('/api/version')
@yamlerrors
def apiVersion(user = Depends(validatedUser)):
    return yamlfy(
        version = version,
        variant = os.environ.get('TOMATIC_VARIANT', 'tomatic')
    )

@app.post('/api/logger/{event}')
@ayamlerrors
async def logger(request: Request, event: str):
    print("RUNNING")
    log = ns.loads(await request.body())
    user = log.get('user', 'anonymous')
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    logline = f"{timestamp}\t{event}\t{user}\n"
    print(logline)
    with Path('usagelog.log').open('a') as logfile:
        logfile.write(logline)
    return yamlfy(
        result = 'ok',
    )

@app.get('/api/graella/list')
@yamlerrors
def listGraelles(user = Depends(validatedUser)):
    return yamlfy(weeks=schedules.list())

@app.get('/api/graella/retireold')
@yamlerrors
def retireOldTimeTable(user = Depends(validatedUser)):
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


@app.get('/api/graella-{week}.yaml')
@app.get('/api/graella/{week}')
@yamlerrors
def graellaYaml(week, user = Depends(validatedUser)):
    schedule = schedules.load(week)

    return yamlfy(**schedule)

@app.patch('/api/graella/{week}/{day}/{houri}/{turni}/{name}')
@ayamlerrors
async def editSlot(week, day, houri: int, turni: int, name, request: Request, user = Depends(validatedUser)):
    # TODO: This should be some kind of auth
    user = (await request.body()).decode('utf8').split('"')[1]
    graella = schedules.load(week)
    # TODO: Ensure day, houri, turni and name are in graella
    oldName = graella.timetable[day][int(houri)][int(turni)]
    if name == 'ningu' and occurrencesInTurn(graella, day, houri, name) == CONFIG.maxNingusPerTurn:
        raise ApiError("Hi ha masses Ningu en aquest torn")
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
    step(logmsg)
    graella.setdefault('log',[]).append(logmsg)
    schedules.save(graella)
    schedulestorage.publishStatic(graella)
    return graellaYaml(week)


def cachedQueueStatus(force=False):
    now = datetime.now()
    if not force and hasattr(cachedQueueStatus, 'value') and cachedQueueStatus.timestamp > now:
        return cachedQueueStatus.value
    cachedQueueStatus.timestamp = now + timedelta(seconds=5)
    cachedQueueStatus.value = pbx().queue()
    return cachedQueueStatus.value

@app.post('/api/graella')
@yamlerrors
def uploadGraella(yaml: UploadFile = File(...), week=None, user = Depends(validatedUser)):
    step("uploading {}".format(yaml.filename))
    graella = ns.load(yaml.file)
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

@app.get('/api/queue')
@yamlerrors
def get_queue(user = Depends(validatedUser)):
    return yamlfy(
        currentQueue = cachedQueueStatus()
    )

@app.get('/api/queue/add/{person}')
@yamlerrors
def add_line(person, user = Depends(validatedUser)):
    p = pbx()
    p.add(person)
    return yamlfy(
        currentQueue = cachedQueueStatus(force=True)
    )

@app.get('/api/queue/pause/{person}')
@yamlerrors
def pause_line(person, user = Depends(validatedUser)):
    p = pbx()
    p.pause(person)
    return yamlfy(
        currentQueue = cachedQueueStatus(force=True)
    )

@app.get('/api/queue/resume/{person}')
@yamlerrors
def resume_line(person, user = Depends(validatedUser)):
    p = pbx()
    p.resume(person)
    return yamlfy(
        currentQueue = cachedQueueStatus(force=True)
    )

@app.get('/api/persons/extension/{extension}')
@yamlerrors
def personInfoFromExtension(extension, user = Depends(validatedUser)):
    allpersons=persons.persons()
    names = [name for name,ext in allpersons.extensions.items() if ext == extension]
    if not names:
        return 'nobody@somenergia.coop'
    name = names[0]
    email = allpersons.emails[name]
    return email

@app.get('/api/persons')
@yamlerrors
def personInfo(user = Depends(validatedUser)):
    result=persons.persons()
    return yamlfy(persons=result)

@app.post('/api/person/{person}')
@ayamlerrors
async def setPersonInfo(person, request: Request, user = Depends(validatedUser)):
    data = ns.loads(await request.body())
    persons.update(person, data)
    return yamlfy(persons=persons.persons())

@app.get('/api/busy/{person}')
@yamlerrors
def busy(person, user = Depends(validatedUser)):
    from . import busy
    return yamlfy(**busy.busy(person))

@app.post('/api/busy/{person}')
@ayamlerrors
async def busy_post(person, request: Request, user = Depends(validatedUser)):
    from . import busy
    data = ns.loads(await request.body())
    return yamlfy(**busy.update_busy(person, data))

@app.get('/api/busy/download/weekly')
@yamlerrors
def downloadWeeklyBusy(user = Depends(validatedUser)):
    response = FileResponse(
        path='indisponibilitats.conf',
        #as_attachment=True,
        media_type='text/plain',
    )
    return response

@app.get('/api/busy/download/oneshot')
@yamlerrors
def downloadOneShotBusy(user = Depends(validatedUser)):
    return FileResponse(
        'oneshot.conf',
        #as_attachment=True,
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
def downloadShiftLoad(week, user = Depends(validatedUser)):
    loadfile = Path('carrega-{}.csv'.format(week))

    return FileResponse(
        str(loadfile),
        #as_attachment=True,
        media_type='text/csv',
    )

@app.get('/api/shifts/download/overload/{week}')
def downloadOverload(week, user = Depends(validatedUser)):
    loadfile = Path('overload-{}.yaml'.format(week))

    return FileResponse(
        str(loadfile),
        #as_attachment=True,
        media_type = 'application/x-yaml',
    )

def yamlinfoerror(code, message, *args, **kwds):
    error(message, *args, **kwds)
    return yamlfy(info=ns(
        info='',
        message=code,
    ))

@app.get('/api/info/{field}/{value}')
@yamlerrors
def getInfoPersonBy(field, value, user = Depends(validatedUser)):
    decoded_value = urllib.parse.unquote(value)
    data = None
    with erp() as O:
        callinfo = CallInfo(O)
        try:
            data = callinfo.getByField(field, decoded_value, shallow=True)
        except ValueError:
            return yamlinfoerror('error_getBy'+field.title(),
                "Getting information searching {}='{}'.", field, value)
    if data is None:
        return 404
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
async def getContractDetails(request: Request, user = Depends(validatedUser)):
    params = ns.loads(await request.body())
    with erp() as O:
        info = CallInfo(O)
        data = info.contractDetails(params.contracts)

    result = ns(
        info=data,
        message='ok',
    )
    return yamlfy(info=result)


@app.get('/api/info/ringring')
async def callingPhone(phone: str, extension: str):
    return await notifyIncommingCall(phone, extension)

@app.post('/api/info/ringring')
async def callingPhonePost(phone: str = Form(...), ext: str = Form(...)):
    return await notifyIncommingCall(phone, ext)

async def notifyIncommingCall(phone: str, extension: str):
    time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    user = persons.byExtension(extension)
    phone = phone.replace('+','').replace('-','').replace(' ','')
    phone = re.sub(r'^[+]?0?0?34','', phone)
    CallRegistry().annotateCall(ns(
        user = user,
        date = time,
        phone = phone,
        partner = '',
        contract = '',
        reason = '',
    ))
    notifications = backchannel.notifyIncommingCall(user, phone, time)
    if not notifications:
        warn(
            f"No sesion on extension {extension} "
            f"to notify incomming call from {phone} at {time}")
    await asyncio.gather(*notifications)
    return yamlfy(result='ok')


@app.get('/api/personlog')
@app.get('/api/personlog/{user}')
def getCallLog(user=None, validatedUser = Depends(validatedUser)):
    calls = CallRegistry().callsByUser(user or validatedUser)
    return yamlfy(
        info=ns(
            info=calls,
            message='ok',
        )
    )


@app.post('/api/call/annotate')
async def callAnnotate(request: Request, user = Depends(validatedUser)):
    annotation = ns.loads(await request.body())
    CallRegistry().annotateCall(annotation)
    user = annotation.get('user', None)
    if user:
        await asyncio.gather(
            *backchannel.notifyCallLogChanged(user)
        )
    return yamlfy(info=ns(
        message="ok"
    ))

@app.get('/api/call/categories')
def annotationCategories(user = Depends(validatedUser)):
    categories = CallRegistry().annotationCategories()
    return yamlfy(**categories)

@app.get('/api/call/categories/update')
def updateClaimTypes(user = Depends(validatedUser)):
    with erp() as O:
        CallRegistry().updateAnnotationCategories(O)
    return yamlfy(info=ns(message='ok'))

@app.get('/api/calendar/{person}')
def icalendar(person):
    calendar = schedules.personIcs(person)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter(calendar),
        200,
        media_type = 'text/calendar',
    )



# vim: ts=4 sw=4 et
