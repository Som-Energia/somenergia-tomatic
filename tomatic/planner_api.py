# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()
import datetime
import decorator
from consolemsg import step, warn, u, b
from flask import (
    Blueprint,
    redirect,
    request,
    send_file,
    url_for,
    )
from .execution import PlannerExecution, nextMonday

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


api = Blueprint("planner_execution", __name__)

@decorator.decorator
def nocache(f, *args, **kwds):
    r = f(*args, **kwds)
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@api.route('/')
def default():
    return redirect(url_for('.list'), code=303)

@api.route('/list')
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
        now = datetime.datetime.utcnow()
        return ("""\
            <tr>
            <td>{startTime}</td>
            <td><a href='status/{name}'>{name}</a></td>
            <td>{state}</td>
            <td><a href='solution/{name}'>{completedCells}/{totalCells}</a></td>
            <td>{unfilledCell}</td>
            <td>{solutionCost}</td>
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
            ))

    return "\n".join([
        """<p><form action='run' method='post'>"""
            """Dilluns&nbsp;(YYYY-MM-DD):&nbsp;<input name=monday type=text value={nexmonday} /><br/>"""
            """Linies:&nbsp;<input name=nlines type=text value=7 /><br/>"""
            """Descripció:&nbsp;<input name=description type=text /><br/>"""
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
        """.format(nexmonday=nextMonday())
    ]+[
        executionDescription(execution.listInfo())
        for execution in PlannerExecution.list()
    ]+[
        """</table>"""
    ])

@api.route('/run', methods=['POST'])
@nocache
def run():
    nlines = request.form.get('nlines')
    if nlines is not None:
        nlines = int(nlines)
    execution = PlannerExecution.start(
        monday=request.form.get('monday',''),
        description=request.form.get('description',''),
        nlines=nlines,
    )
    return redirect(url_for('.list'), code=303)

@api.route('/status/<execution>')
def status(execution):
    import deansi
    executionOutput = PlannerExecution(execution).outputFile
    return u"<style>pre {{ background-color: white; color: black}} {style} </style><pre>{content}</pre>".format(
        style = deansi.styleSheet(),
        content = deansi.deansi(executionOutput.read_text(encoding='utf8'))
    )
        

@api.route('/solution/<execution>')
@nocache
def solution(execution):
    solution = PlannerExecution(execution).solutionHtml.resolve()
    return send_file(solution.open('rb'), mimetype='text/html', cache_timeout=2)

@api.route('/stop/<execution>')
def stop(execution):
    execution = PlannerExecution(execution)
    step("Stopping {0.pid} {0.name}", execution)
    if not execution.stop():
        warn("Process {} not found", execution.pid)
    return redirect(url_for('.list'), code=303)

@api.route('/kill/<execution>')
def kill(execution):
    execution = PlannerExecution(execution)
    step("Killing {0.pid} {0.name}", execution)
    if not execution.kill():
        warn("Process {} not found", execution.pid)
    return redirect(url_for('.list'), code=303)

@api.route('/remove/<execution>')
def remove(execution):
    execution = PlannerExecution(execution)
    step("Cleaning up {0.name}", execution)
    if not execution.remove():
        warn("Process {} not finished", execution.pid)
    return redirect(url_for('.list'), code=303)

@api.route('/upload/<execution>')
def upload(execution):
    execution = PlannerExecution(execution)
    step("Uploading {0.name}", execution)
    execution.upload('nobody') # TODO: Take ERP user
    return redirect(url_for('.list'), code=303)


if __name__ == '__main__':
    from flask import Flask
    app = Flask("Background planner runner")
    app.register_blueprint(api)
    PlannerExecution.ensureRootExists()
    app.run(host='0.0.0.0', debug=True)


# vim: ts=4 sw=4 et
