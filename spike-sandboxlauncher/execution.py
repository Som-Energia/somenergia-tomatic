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

import os
import signal
import errno
import subprocess
import uuid
import datetime
from pathlib2 import Path
from consolemsg import step, success, warn
from yamlns import namespace as ns

executionRoot = Path('executions')

class Execution(object):

    @staticmethod
    def start(name=None, command=None):
        executionName = "{}-{}".format(datetime.datetime.now(), uuid.uuid4())
        execution = Execution(executionName)
        step("Running task '{}'", executionName )
        execution.path.mkdir()
        command = "../../example.sh /usr".split()
        #command = "launcherwrapper.sh tomatic_scheduler.py afasdflkjas "
        step("Running {}", command)
        log = execution.outputFile.open('w')
        process = subprocess.Popen(
            command,
            #shell=True,
            cwd=str(execution.path),
            stdout=log,
            stderr=log,
        )
        success("Running child: {}", process.pid)
        #(execution.path / 'pid').write_text(u(process.pid))
        return executionName

    @staticmethod
    def list():
        return (
            Execution(executiondir.name)
            for executiondir in sorted(executionRoot.iterdir(), reverse=True)
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
                print(type(err))
                return
            raise

    @property
    def outputFile(self):
        return self.path / 'output.txt'

    def listInfo(self):
        return ns(
            name = self.name,
            killDisplay = 'inline' if self.state == 'Running' else 'none',
            state = self.state,
            )



# vim: ts=4 sw=4 et
