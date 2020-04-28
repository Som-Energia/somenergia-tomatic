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

app = Flask("Background runner")

from execution import Execution


@app.route('/')
def default():
    return redirect('/list')

@app.route('/list')
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

@app.route('/run')
def run():
    execution = Execution.start()
    return redirect("/list".format(execution))

@app.route('/status/<execution>')
def status(execution):
    executionOutput = Execution(execution).outputFile
    return send_file(str(executionOutput))

@app.route('/stop/<execution>')
def stop(execution):
    execution = Execution(execution)
    execution.stop()
    return redirect("/list", code=302)


app.run()

# vim: ts=4 sw=4 et
