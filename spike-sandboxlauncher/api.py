# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()

from consolemsg import step, warn
from flask import (
    Flask,
    Blueprint,
    redirect,
    send_file,
    )
from execution import Execution

api = Blueprint("Background runner", __name__)

@api.route('/')
def default():
    return redirect('/list')

@api.route('/list')
def list():
    return  "\n".join([
        """<p><a href='/run'>New</a></p>"""
    ]+[
        """\
        <li>
            <a href='/status/{name}'>{name}</a>
            {state}
            <a style='display:{killDisplay}' href='/stop/{name}'>Stop</a>
            <a style='display:{removeDisplay}' href='/remove/{name}'>Remove</a>
        </li>
        """.format(**execution.listInfo())
        for execution in Execution.list()
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
