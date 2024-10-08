# -*- coding: utf-8 -*-

import datetime
import decorator
from consolemsg import step, warn, u, b
from yamlns import ns
from fastapi import(
    FastAPI,
    APIRouter,
    Form,
    Request,
    HTTPException,
)
from fastapi.responses import (
    Response,
    RedirectResponse,
    HTMLResponse,
    FileResponse,
)

from .plannerexecution import PlannerExecution, nextMonday

# TODO: Dupped from tomatic/api.py
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

def humanDuration(seconds):
    units = [
        ('week', 7*24*60*60),
        ('days', 24*60*60),
        ('h', 60*60),
        ('m', 60),
        ('s', 1),
    ]
    unitNames = [x[0] for x in units]
    unitSeconds=dict(units)
    for bigger, lesser in zip(unitNames, unitNames[1:]):
        if seconds < unitSeconds[bigger]: continue
        manyBigger = seconds // unitSeconds[bigger]
        remainding = seconds % unitSeconds[bigger]
        manyLesser = remainding // unitSeconds[lesser]
        return "{} {} {} {}".format(
            manyBigger, bigger,
            manyLesser, lesser,
        )
    return "{} seconds".format(seconds)


api = APIRouter()

@decorator.decorator
def nocache(f, *args, **kwds):
    r = f(*args, **kwds)
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@api.get('/list', name='thelist', response_class=HTMLResponse)
def list():
    def executionDescription(info):
        killAction = ("""<a href='kill/{name}'>Kill</a> """
            if info.state == 'Running' else '')
        stopAction = ("""<a href='stop/{name}'>Stop</a> """
            if info.state == 'Running' else '')
        removeAction = ("""<a href='remove/{name}'>Remove</a> """
            if info.state == 'Stopped' else '')
        uploadAction = ("""<a href='upload/{name}'>Upload</a> """
            if info.completedCells
            and info.completedCells == info.totalCells
            else '')
        busyReasons = "".join([
            """<div class=tooltip>"""
            """<h3>Indisponibilitats de {}</h3>""".format(info.unfilledCell)
            ]+[
                "<b>{name}:</b> {reason}<br>"
                    .format(name=u(name), reason=u(reason))
                for name, reasons in info.busyReasons.items()
                for reason in reasons
            ]+[
            """</div>"""
        ]) if info.busyReasons else ""
        penalties = "".join([
            """<div class=tooltip>"""
            """<h3>Penalitzacions</h3>"""
            ]+[
                "<b>{penalty}:</b> {reason}<br>"
                    .format(penalty=u(penalty), reason=u(reason))
                for penalty, reason in info.get('penalties',[])
            ]+[
            """</div>"""
        ])
        now = datetime.datetime.utcnow()
        return ("""\
            <tr>
            <td>{startTime}</td>
            <td><a href='status/{name}'>{name}</a></td>
            <td>{state}</td>
            <td><a href='solution/{name}'>{completedCells}/{totalCells}</a></td>
            <td>{unfilledCell} {busyReasons}</td>
            <td>{solutionCost} {penalties}</td>
            <td>{timeSinceLastSolution}</td>
            <td>
        """ + stopAction + uploadAction + removeAction + killAction + """</td>
        </tr>
        """).format(**dict(
                info,
                startTime = u(info.startTime)[:len('YYYY-MM-DD HH:MM:SS')],
                timeSinceLastSolution = "fa {}".format(
                    humanDuration((now-info.timeOfLastSolution).seconds)) if info.timeOfLastSolution else "--",
                completedCells = info.completedCells or '--',
                totalCells = info.totalCells or '--',
                solutionCost = info.solutionCost or '--',
                unfilledCell = info.unfilledCell or '??',
                busyReasons = busyReasons,
                penalties = penalties,
            ))

    return "\n".join([
        """<style>"""
            """.tooltip {{ visibility: hidden; position:absolute; cursor: link; width: 20em; background: #ffa; border: 1px solid grey; padding:1ex}}"""
            """td:hover .tooltip {{ visibility: visible}}</style>"""
        """<p><form action='run' method='post'>"""
            """<label>Setmana:&nbsp;<input name=monday type=date value={nexmonday} step=7 required /></label><br/>"""
            """<label>Linies:&nbsp;<input name=nlines type=number value={nlines} step=1 required/></label><br/>"""
            """<label>Descripció:&nbsp;<input name=description type=text /></label><br/>"""
            """<label>Dies a omplir primer:&nbsp;<input name="search_days" type=text /> (dl, dm, dx, dj, dv, separats per comes)</label><br/>"""
            """<input type=submit value='Llençar' />"""
        """</form></p>"""
        """<p><a href='clear'>Clear</a></p>"""
        """<table width=100%>"""
        """
            <tr>
            <th>Start time</th>
            <th>Name</th>
            <th>State</th>
            <th>Completion</th>
            <th>Celda bloqueo</th>
            <th>Cost</th>
            <th>Darrera bona</th>
            <th>Actions</th>
            </tr>
        """.format(
            nexmonday=nextMonday(),
            nlines=8, #TODO: config.nTelefons,
        )
    ]+[
        executionDescription(execution.listInfo())
        for execution in PlannerExecution.list()
    ]+[
        """</table>"""
    ])

def gotoList(request):
    url = request.url_for('thelist')
    return RedirectResponse(url, status_code=303)

@api.get('/')
def default(request: Request):
    return gotoList(request)

@api.post('/run')
@nocache
def run(
    request: Request,
    nlines: int = Form(None),
    monday: str = Form(''),
    search_days: str = Form(''),
    description: str = Form(''),
):
    if nlines is not None:
        nlines = int(nlines)
    execution = PlannerExecution.start(
        monday=monday,
        description=description,
        nlines=nlines,
        searchDays=search_days,
    )
    return gotoList(request)


@api.get('/status/{execution}', response_class=HTMLResponse)
def status(execution):
    import deansi
    executionOutput = PlannerExecution(execution).outputFile
    return u"<style>pre {{ background-color: white; color: black}} {style} </style><pre>{content}</pre>".format(
        style = deansi.styleSheet(),
        content = deansi.deansi(executionOutput.read_text(encoding='utf8'))
    )
        

@api.get('/solution/{execution}', response_class=HTMLResponse)
@nocache
def solution(execution):
    solution = PlannerExecution(execution).solutionHtml.resolve()
    if not solution.exists():
        raise HTTPException(404)
    return FileResponse( solution, media_type='text/html',
        #headers=dict(cache_timeout="2"), # Not fully migrated from Flask
    )

@api.get('/stop/{execution}')
def stop(request: Request, execution):
    execution = PlannerExecution(execution)
    step("Stopping {0.pid} {0.name}", execution)
    if not execution.stop():
        warn("Process {} not found", execution.pid)
    return gotoList(request)

@api.get('/kill/{execution}')
def kill(request: Request, execution):
    execution = PlannerExecution(execution)
    step("Killing {0.pid} {0.name}", execution)
    if not execution.kill():
        warn("Process {} not found", execution.pid)
    return gotoList(request)

@api.get('/remove/{execution}')
def remove(request: Request, execution):
    execution = PlannerExecution(execution)
    step("Cleaning up {0.name}", execution)
    if not execution.remove():
        warn("Process {} not finished", execution.pid)
    return gotoList(request)

@api.get('/upload/{execution}')
def upload(request: Request, execution):
    execution = PlannerExecution(execution)
    step("Uploading {0.name}", execution)
    execution.upload('nobody') # TODO: Take ERP user
    return gotoList(request)

# Follows the non page based api

@api.get('/api/list')
@nocache
def list():
    return yamlfy(tasks=[
        task.listInfo()
        for task in PlannerExecution.list()
    ])

@api.post('/api/run')
@nocache
def run(
    request: Request,
    nlines: int,
    monday: str,
    description: str,
):
    if nlines is not None:
        nlines = int(nlines)
    execution_id = PlannerExecution.start(
        monday=monday,
        description=description,
        nlines=nlines,
    )
    return yamlfy(execution_id=execution_id)

@api.get('/api/status/{execution_id}')
@nocache
def status(
    request: Request,
    execution_id: str,
):
    execution = PlannerExecution(execution_id)
    return yamlfy(**execution.listInfo())

@api.get('/api/stop/{execution_id}')
def stop(request: Request, execution_id):
    execution = PlannerExecution(execution_id)
    step("Stopping {0.pid} {0.name}", execution)
    if not execution.stop():
        return yamlfy(ok=False)
    return yamlfy(ok=True)

@api.get('/api/kill/{execution_id}')
def kill(request: Request, execution_id):
    execution = PlannerExecution(execution_id)
    step("Killing {0.pid} {0.name}", execution)
    if not execution.kill():
        return yamlfy(ok=False)
    return yamlfy(ok=True)

@api.get('/api/remove/{execution_id}')
def remove(request: Request, execution_id):
    execution = PlannerExecution(execution_id)
    step("Cleaning up {0.name}", execution)
    if not execution.remove():
        return yamlfy(ok=False)
    return yamlfy(ok=True)

@api.get('/api/upload/{execution_id}')
def upload(request: Request, execution_id):
    execution = PlannerExecution(execution_id)
    step("Uploading {0.name}", execution)
    execution.upload('nobody') # TODO: Take ERP user
    return yamlfy(ok=True)


if __name__ == '__main__':
    from fastapi import FastAPI
    import uvicorn
    app = FastAPI()
    app.include_router(api, prefix='/test')
    for route in app.routes:
        step(route.path)
    PlannerExecution.ensureRootExists()
    uvicorn.run(app, host='0.0.0.0')


# vim: ts=4 sw=4 et
