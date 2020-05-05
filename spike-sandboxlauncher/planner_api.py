# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()
import datetime
from consolemsg import step, warn
from flask import (
    Flask,
    Blueprint,
    redirect,
    send_file,
    )
from execution import Execution, PlannerExecution

api = Blueprint("Background runner", __name__)

@api.route('/')
def default():
    return redirect('/list')

@api.route('/list')
def list():
    def executionDescription(executionInfo):
        killAction = """<a href='/stop/{name}'>Stop</a>""" if execution.state == 'Running' else ''
        removeAction = """<a href='/remove/{name}'>Remove</a>""" if execution.state == 'Stopped' else ''
        return ("""\
            <tr>
            <td>{startTime}</td>
            <td><a href='/status/{name}'>{name}</a></td>
            <td>{state}</td>
            <td>{completedCells}/{totalCells}</td>
            <td>{solutionCost}</td>
            <td>{timeSinceLastSolution}</td>
            <td>
        """ + killAction + removeAction + """</td>
        </tr>
        """).format(**dict(
                executionInfo,
                timeSinceLastSolution = (datetime.datetime.utcnow()-executionInfo.timeOfLastSolution).seconds if executionInfo.timeOfLastSolution else "??"
            ))

    return  "\n".join([
        """<p><a href='/run'>New</a></p>"""
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
        """
    ]+[
        executionDescription(execution.listInfo())
        for execution in PlannerExecution.list()
    ]+[
        """</table>"""
    ])

@api.route('/run')
def run():
    execution = Execution.start("../../example.sh /usr".split())
    return redirect("/list".format(execution))

@api.route('/status/<execution>')
def status(execution):
    executionOutput = Execution(execution).outputFile
    return send_file(str(executionOutput))

@api.route('/stop/<execution>')
def stop(execution):
    execution = Execution(execution)
    step("Stopping {0.pid} {0.name}", execution)
    if not execution.stop():
        warn("Process {} not found", execution.pid)
    return redirect("/list", code=302)

@api.route('/remove/<execution>')
def remove(execution):
    execution = Execution(execution)
    step("Cleaning up {0.name}", execution)
    if not execution.remove():
        warn("Process {} not finished", execution.pid)
    return redirect("/list", code=302)


if __name__ == '__main__':
    app = Flask("Background runner")
    app.register_blueprint(api)
    Execution.ensureRootExists()
    app.run()


# vim: ts=4 sw=4 et
