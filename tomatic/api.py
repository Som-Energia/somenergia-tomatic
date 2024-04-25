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
    HTTPException,
)
from fastapi.responses import (
    FileResponse,
    Response,
    RedirectResponse,
)
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import re
import os
from datetime import datetime, timedelta, timezone
import urllib.parse
import decorator
import inspect
import erppeek
from pathlib import Path
from yamlns import namespace as ns
from consolemsg import error, step, warn, u

from . import __version__ as version
from . import callinfo
from .callregistry import CallRegistry
from .call_registry.models import NewCall, Call
from . import schedulestorage
from . import schedulestorageforcedturns
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
forcedTurns = schedulestorageforcedturns.Storage()

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
from .auth import router as Auth, validatedUser, userInGroup
from fastapi.websockets import WebSocket

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="Hola, Supers!")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(Planner, prefix='/api/planner')
app.include_router(Auth, prefix='/api/auth')

class ApiError(Exception): pass

def requireAdmin(user, message="Only admins can perform this operation"):
    if not userInGroup(user, 'admin'):
        raise HTTPException(
            status_code=403,
            detail=message,
        )

def yamlfy(status=200, data=[], **kwd):
    output = ns(data, **kwd)
    return Response(output.dump(),
        status,
        media_type = 'application/x-yaml',
    )

@decorator.decorator
async def yamlerrors(f,*args,**kwd):
    try:
        result = f(*args,**kwd)
        if inspect.isawaitable(result):
            return await result
        return result
    except ApiError as e:
        error("ApiError: {}", e)
        return yamlfy(
            error=format(e),
            status=400,
            )
    except HTTPException:
        raise
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
def web_site(request: Request, file=None):
    return FileResponse(distpath / (file or 'index.html'))

@app.get('/static/{dir}/{file}')
def static_files(request: Request, file=None, dir=None):
    return FileResponse(distpath / 'static' / dir / (file or 'index.html'))

@app.get('/api/version')
@yamlerrors
def api_version():
    return yamlfy(
        version = version,
        variant = os.environ.get('TOMATIC_VARIANT', 'tomatic')
    )

def log_user_event(user, event):
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    logline = f"{timestamp}\t{event}\t{user}\n"
    print(logline)
    statsDir = Path('stats')
    statsDir.mkdir(exist_ok=True)
    with (statsDir/'usagelog.log').open('a') as logfile:
        logfile.write(logline)

@app.post('/api/logger/{event}')
@yamlerrors
async def user_event_logger(request: Request, event: str):
    "records an event for the user for instrumentation"
    log = ns.loads(await request.body())
    user = log.get('user', 'anonymous')
    log_user_event(user, event)
    return yamlfy(
        result = 'ok',
    )

@app.get('/api/graella/list')
@yamlerrors
def timetable_list(user = Depends(validatedUser)):
    return yamlfy(weeks=schedules.list())

@app.get('/api/graella/retireold')
@yamlerrors
def retire_old_timetables(user = Depends(validatedUser)):
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

@app.get('/api/forcedturns')
@yamlerrors
async def forced_turns(user = Depends(validatedUser)):
    timetable = forcedTurns.load()
    return yamlfy(**timetable)

@app.patch('/api/forcedturns/{day}/{houri}/{turni}/{name}')
@yamlerrors
async def forced_turns_edit_slot(day, houri: int, turni: int, name, request: Request, user = Depends(validatedUser)):
    user=user['username']
    try:
        forcedTurns.editSlot(day, houri, turni, name, user)
    except schedulestorageforcedturns.BadEdit as e:
        raise ApiError(str(e))
    return await forced_turns()

# TODO: Remove casing in urls
@app.patch('/api/forcedturns/addColumn', deprecated=True)
@app.patch('/api/forcedturns/line/add')
@yamlerrors
async def forcedturns_add_line():
    try:
        forcedTurns.addColumn()
    except schedulestorageforcedturns.BadEdit as e:
        raise ApiError(str(e))
    return await forced_turns()

# TODO: Remove casing in urls
@app.patch('/api/forcedturns/removeColumn', deprecated=True)
@app.patch('/api/forcedturns/line/remove')
@yamlerrors
async def forced_turns_delete_line():
    try:
        forcedTurns.removeColumn()
    except schedulestorageforcedturns.BadEdit as e:
        raise ApiError(str(e))
    return await forced_turns()

@app.get('/api/graella-{week}.yaml')
@app.get('/api/graella/{week}')
@yamlerrors
def timetable(week, user = Depends(validatedUser)):
    schedule = schedules.load(week)

    return yamlfy(**schedule)

@app.patch('/api/graella/{week}/{day}/{houri}/{turni}/{name}')
@yamlerrors
async def edit_timetable_slot(week, day, houri: int, turni: int, name, request: Request, user = Depends(validatedUser)):
    #user = (await request.body()).decode('utf8').split('"')[1]
    user=user['username']
    try:
        schedules.editSlot(week, day, houri, turni, name, user)
    except schedulestorage.BadEdit as e:
        raise ApiError(str(e))
    return await timetable(week)


def cachedQueueStatus(force=False):
    now = datetime.now()
    if not force and hasattr(cachedQueueStatus, 'value') and cachedQueueStatus.timestamp > now:
        return cachedQueueStatus.value
    cachedQueueStatus.timestamp = now + timedelta(seconds=5)
    cachedQueueStatus.value = pbx().queue()
    return cachedQueueStatus.value

@app.post('/api/graella')
@yamlerrors
def upload_timetable(yaml: UploadFile = File(...), week=None, user = Depends(validatedUser)):
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

@app.get('/api/persons')
@yamlerrors
def person_info():
    result=persons.persons()
    return yamlfy(persons=result)

@app.post('/api/person/{person}')
@yamlerrors
async def set_person_info(person, request: Request, user = Depends(validatedUser)):
    data = ns.loads(await request.body())
    if person != user.username:
        requireAdmin(user)
    persons.update(person, data)
    return yamlfy(persons=persons.persons())

@app.delete('/api/person/{person}')
@yamlerrors
async def delete_person(person, user = Depends(validatedUser)):
    requireAdmin(user)
    persons.delete(person)
    return yamlfy(persons=persons.persons())

@app.get('/api/busy/{person}')
@yamlerrors
def busy(person, user = Depends(validatedUser)):
    "Get person's busy hours"
    from . import busy
    return yamlfy(**busy.busy(person))

@app.post('/api/busy/{person}')
@yamlerrors
async def set_busy(person, request: Request, user = Depends(validatedUser)):
    "Set person's busy hours"
    from . import busy
    data = ns.loads(await request.body())
    return yamlfy(**busy.update_busy(person, data))

@app.get('/api/busy/download/weekly')
@yamlerrors
def download_weekly_busy_hours_file(): # TODO requires validation
    response = FileResponse(
        path='indisponibilitats.conf',
        #as_attachment=True,
        media_type='text/plain',
    )
    return response

@app.get('/api/busy/download/oneshot')
@yamlerrors
def download_one_shot_busy_hours_file(): # TODO requires validation
    return FileResponse(
        'oneshot.conf',
        #as_attachment=True,
        media_type='text/plain',
    )

@app.get('/api/shifts/download/credit/{week}')
@yamlerrors
def download_week_shift_credit(week): # TODO requires validation
    try:
        credit = schedules.credit(week)
    except schedulestorage.StorageError as e:
        raise ApiError(e)
    return yamlfy(**credit)

def yamlinfoerror(code, message, *args, **kwds):
    error(message, *args, **kwds)
    return yamlfy(info=ns(
        info='',
        message=code,
    ))

@app.get('/api/info/{field}/{value}')
@yamlerrors
def customer_info(field: callinfo.SearchField, value: str, user = Depends(validatedUser)):
    "Retrieves customer information"
    decoded_value = urllib.parse.unquote(value)
    data = None
    with erp() as O:
        info = callinfo.CallInfo(O)
        try:
            data = info.getByField(field, decoded_value, shallow=True)
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
async def contract_details(request: Request, user = Depends(validatedUser)):
    "Returns lesser or slower details of the contracts"
    params = ns.loads(await request.body())
    with erp() as O:
        info = callinfo.CallInfo(O)
        data = info.contractDetails(params.contracts)

    result = ns(
        info=data,
        message='ok',
    )
    return yamlfy(info=result)


@app.get('/api/info/ringring')
async def notify_incomming_call(
    phone: str,
    extension: str,
    callid: str = None,
):
    """
    Notifies (from a pbx) that there is an incomming call
    from the phone number to the extension
    """
    return await notifyIncommingCall(phone, extension, callid)

@app.post('/api/info/ringring')
async def notify_incomming_call(
    phone: str = Form(...),
    ext: str = Form(...),
    callid: str = Form(None)
):
    """
    Notifies (from a pbx) that there is an incomming call
    from the phone number to the extension
    """
    return await notifyIncommingCall(phone, ext, callid)

def cleanupPhone(phone):
    phone = re.sub('[^0-9]', '', phone) # remove non digits
    phone = re.sub(r'^0?0?34','', phone) # remove prefixes
    return phone

async def notifyIncommingCall(phone: str, extension: str, callid: str = None):
    time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    user = persons.byExtension(extension)
    phone = cleanupPhone(phone)
    pbx_call_id = callid or f"{time}-{phone}"

    # TODO: cleanup old call registration
    CallRegistry().annotateCall(ns(
        user = user,
        date = time,
        phone = phone,
        partner = '',
        contract = '',
        reason = '',
    ))

    from .call_registry import CallRegistry as NewCallRegistry
    NewCallRegistry().add_incoming_call(
        NewCall(
            operator=user,
            call_timestamp=time,
            phone_number=phone,
            pbx_call_id=pbx_call_id,
        )
    )

    notifications = backchannel.notifyIncommingCall(user, phone, time)
    if not notifications:
        warn(
            f"No sesion on extension {extension} "
            f"to notify incomming call from {phone} at {time}")
    await asyncio.gather(*notifications)
    return yamlfy(result='ok')

@app.get('/api/call/log')
@app.get('/api/call/log/{user}')
def get_user_call_log(user=None, validatedUser = Depends(validatedUser)):
    from .call_registry import CallRegistry as NewCallRegistry
    calls = NewCallRegistry().get_calls(operator=user or validatedUser.get('username'))
    return yamlfy(**calls.model_dump())

@app.post('/api/call/annotate')
async def annotate_call(request: Request, user = Depends(validatedUser)):
    "Annotates a call"
    call = ns.loads(await request.body())
    from .call_registry import CallRegistry as NewCallRegistry
    annotation = Call(**call)
    call = NewCallRegistry().modify_existing_call(annotation)
    return yamlfy(**call.model_dump())

@app.get('/api/call/categories')
def call_annotation_categories(user = Depends(validatedUser)):
    "Returns a list of categories to annotate calls"
    from .call_registry import CallRegistry as NewCallRegistry
    categories = NewCallRegistry().categories()
    return yamlfy(**categories.model_dump())

@app.get('/api/calendar/{person}')
def shift_calendar(person):
    "Returns an ical with the attention shifts of the person"
    log_user_event(person, "calendarRefresh")
    calendar = schedules.personIcs(person)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter(calendar),
        200,
        media_type = 'text/calendar',
    )

@app.post('/api/tomatic/says')
@yamlerrors
async def tomatic_says(
    request: Request,
    user = Depends(validatedUser)
):
    data = ns.loads(await request.body())
    from .directmessage.tomatic_webhook import send
    if not dbconfig.tomatic.get("monitorChatChannel"):
        return ApiError("No direct channel conrigured")
    if not data.get('message') :
        return ApiError("Empty message", 403)
    send(
        dbconfig.tomatic.monitorChatChannel,
        data.message
    )
    return yamlfy(result="ok")


# vim: ts=4 sw=4 et
