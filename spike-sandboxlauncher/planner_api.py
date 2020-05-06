# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()
import datetime
from consolemsg import step, warn, u
from flask import (
    Flask,
    Blueprint,
    redirect,
    request,
    send_file,
    )
from execution import PlannerExecution, nextMonday

api = Blueprint("PlannerExecution", __name__)

@api.route('/')
def default():
    return redirect('/list')

@api.route('/list')
def list():
    def executionDescription(info):
        killAction = ("""<a href='/stop/{name}'>Stop</a>"""
            if info.state == 'Running' else '')
        removeAction = ("""<a href='/remove/{name}'>Remove</a>"""
            if info.state == 'Stopped' else '')
        uploadAction = ("""<a href='/upload/{name}'>Upload</a>"""
            if info.completedCells
            and info.completedCells == info.totalCells
            else '')
        now = datetime.datetime.utcnow()
        return ("""\
            <tr>
            <td>{startTime}</td>
            <td><a href='/status/{name}'>{name}</a></td>
            <td>{state}</td>
            <td><a href='/solution/{name}'>{completedCells}/{totalCells}</a></td>
            <td>{solutionCost}</td>
            <td>{timeSinceLastSolution}</td>
            <td>
        """ + killAction + uploadAction + removeAction + """</td>
        </tr>
        """).format(**dict(
                info,
                startTime = u(info.startTime)[:len('YYYY-MM-DD HH:MM:SS')],
                timeSinceLastSolution = "fa {} segons".format(
                    (now-info.timeOfLastSolution).seconds) if info.timeOfLastSolution else "--",
                completedCells = info.completedCells or '--',
                totalCells = info.totalCells or '--',
                solutionCost = info.solutionCost or '--',
            ))

    return  "\n".join([
        """<p><form action='/run' method='post'>"""
            """Dilluns&nbsp;(YYYY-MM-DD):&nbsp;<input name=monday type=text value={nexmonday} /><br/>"""
            """Linies:&nbsp;<input name=nlines type=text value=7 /><br/>"""
            """Descripció:&nbsp;<input name=description type=text /><br/>"""
            """<input type=submit value='Llençar' />"""
        """</form></p>"""
        """<p><a href='/clear'>Clear</a></p>"""
        """<table width=100%>"""
        """
            <tr>
            <th>Start time</th>
            <th>Name</th>
            <th>State</th>
            <th>Completion</th>
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
def run():
    execution = PlannerExecution.start(
        monday=request.form.get('monday',''),
        description=request.form.get('description',''),
    )
    return redirect("/list".format(execution))

@api.route('/status/<execution>')
def status(execution):
    executionOutput = PlannerExecution(execution).outputFile
    return send_file(str(executionOutput))

@api.route('/solution/<execution>')
def solution(execution):
    executionOutput = PlannerExecution(execution).solutionHtml
    return send_file(str(executionOutput))

@api.route('/stop/<execution>')
def stop(execution):
    execution = PlannerExecution(execution)
    step("Stopping {0.pid} {0.name}", execution)
    if not execution.stop():
        warn("Process {} not found", execution.pid)
    return redirect("/list", code=302)

@api.route('/remove/<execution>')
def remove(execution):
    execution = PlannerExecution(execution)
    step("Cleaning up {0.name}", execution)
    if not execution.remove():
        warn("Process {} not finished", execution.pid)
    return redirect("/list", code=302)


if __name__ == '__main__':
    app = Flask("Background runner")
    app.register_blueprint(api)
    PlannerExecution.ensureRootExists()
    app.run()


# vim: ts=4 sw=4 et
