# -*- coding: utf-8 -*-

"""
TODO:
- Obtain scheduler's pid
- Send a signal to the scheduler
- Function to create sandbox
- Current path
- Wrapper para controlar ejecucion
    - Standard error
    - Exit code
"""

from future import standard_library
standard_library.install_aliases()

from flask import (
    Flask,
    Blueprint,
    redirect,
    send_file,
    )
import os
import signal
import errno
import subprocess
import uuid
import datetime
from pathlib2 import Path
from consolemsg import step, success, warn
from yamlns import namespace as ns

api = Blueprint("Background runner", __name__)

from execution import Execution


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
        </li>
        """.format(**execution.listInfo())
        for execution in Execution.list()
    ])

@api.route('/run')
def run():
    execution = Execution.start()
    return redirect("/list".format(execution))

@api.route('/status/<execution>')
def status(execution):
    executionOutput = Execution(execution).outputFile
    return send_file(str(executionOutput))

@api.route('/stop/<execution>')
def stop(execution):
    execution = Execution(execution)
    execution.stop()
    return redirect("/list", code=302)

if __name__ == '__main__':
    app = Flask("Background runner")
    app.register_blueprint(api)
    app.run()


# vim: ts=4 sw=4 et
