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
executionRoot = Path('executions')

class Execution(object):

    @staticmethod
    def start():
        executionName = "{}-{}".format(datetime.datetime.now(), uuid.uuid4())
        execution = Execution(executionName)
        step("Running task {}", executionName )
        execution.path.mkdir()
        command = "../../example.sh /usr > '{}' 2>&1".format(execution.outputFile.name)
        step("running {}", command)
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=str(execution.path),
        )
        success("Running child: ", process.pid)
        return executionName

    @staticmethod
    def list():
        return (
            Execution(execution.name)
            for execution in sorted(executionRoot.iterdir(), reverse=True)
        )

    def __init__(self, name):
        self.name = name
        self.path = executionRoot/name

    @property
    def pid(self):
        if hasattr(self, '_pid'):
            return self._pid
        pidfile = self.path / 'pid'
        if not pidfile.exists():
            return None
        self._pid = int(pidfile.read_text())
        return self._pid

    @property
    def isAlive(self):
        try:
            os.kill(self.pid, signal.SIG_IGN)
        except OSError as err:
            if err.errno == errno.ESRCH: # Process not found
                return False
        return True

    @property
    def state(self):
        if self.pid is None: return 'Launching'
        if self.isAlive: return 'Running'
        return 'Stopped'

    def stop(self):
        warn("Stoping {}", self.pid)
        try:
            os.kill(self.pid, signal.SIGINT)
        except OSError as err:
            if err.errno == errno.ESRCH: # Process not found
                print type(err)
                return
            raise

    @property
    def outputFile(self):
        return self.path / 'caca.txt'

    def listInfo(self):
        return ns(
            name = self.name,
            killDisplay = 'inline' if self.state == 'Running' else 'none',
            state = self.state,
            )

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
