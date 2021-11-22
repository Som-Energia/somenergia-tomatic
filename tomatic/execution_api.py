# -*- coding: utf-8 -*-

from consolemsg import step, warn, u, b
from pathlib import Path
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

from .execution import Execution

api = APIRouter()


@api.get('/list', name='thelist', response_class=HTMLResponse)
def list():
    def executionDescription(executionInfo):
        killAction = """<a href='stop/{name}'>Stop</a>""" if executionInfo.state == 'Running' else ''
        removeAction = """<a href='remove/{name}'>Remove</a>""" if executionInfo.state == 'Stopped' else ''
        return ("""\
            <tr>
            <td>{startTime}</td>
            <td><a href='status/{name}'>{name}</a></td>
            <td>{state}</td>
            <td>
            <td>
        """ + killAction + removeAction + """</td>
        </tr>
        """).format(**executionInfo)

    return  "\n".join([
        """<p><a href='run'>New</a></p>"""
        """<p><a href='clear'>Clear</a></p>"""
        """<table width=100%>"""
        """
            <tr>
            <th>Start time</th>
            <th>Name</th>
            <th>State</th>
            <th>Actions</th>
            </tr>
        """
    ]+[
        executionDescription(execution.listInfo())
        for execution in Execution.list()
    ]+[
        """</table>"""
    ])

def gotoList(request):
    url = request.url_for('thelist')
    return RedirectResponse(url, status_code=303)

@api.get('/')
def default(request: Request):
    return gotoList(request)

@api.get('/run')
def run(request: Request):
    execution = Execution.start([
        Path("execution_example.sh").absolute(),
        "param1",
        "param2",
    ])
    return gotoList(request)

@api.get('/status/{execution}')
def status(execution):
    executionOutput = Execution(execution).outputFile
    return FileResponse(str(executionOutput), media_type='text/plain')

@api.get('/stop/{execution}')
def stop(request: Request, execution):
    execution = Execution(execution)
    step("Stopping {0.pid} {0.name}", execution)
    if not execution.stop():
        warn("Process {} not found", execution.pid)
    return gotoList(request)

@api.get('/remove/{execution}')
def remove(request: Request, execution):
    execution = Execution(execution)
    step("Cleaning up {0.name}", execution)
    if not execution.remove():
        warn("Process {} not finished", execution.pid)
    return gotoList(request)


if __name__ == '__main__':
    from fastapi import FastAPI
    import uvicorn
    app = FastAPI()
    app.include_router(api, prefix='/test')
    for route in app.routes:
        step(route.path)
    Execution.ensureRootExists()
    uvicorn.run(app, host='0.0.0.0')


# vim: ts=4 sw=4 et
