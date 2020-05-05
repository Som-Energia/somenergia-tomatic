# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

"""
TODO:
- Exit code
"""

import os
import signal
import errno
import subprocess
import uuid
import datetime
from pathlib2 import Path
from consolemsg import step, success, warn, u
from yamlns import namespace as ns

executionRoot = Path('executions')
children = {}

def removeRecursive(f):
    if not f.exists() and not f.is_symlink():
        return
    if not f.is_dir():
        f.unlink()
        return
    for sub in f.iterdir():
        removeRecursive(sub)
    f.rmdir()

class Execution(object):

    @staticmethod
    def start(command):
        execution = Execution()
        execution.createSandbox()
        step("Running {}...", execution.name)
        process = execution.run(command)
        step("Process {}...", execution.pid)
        children[process.pid] = process
        return execution.name

    @staticmethod
    def list():
        return [
            Execution(p.name) for p in reversed(sorted(
                executionRoot.iterdir(),
                key=lambda x: x.stat().st_ctime,
            ))
        ]

    def __init__(self, name=None):
        self.name = name or "{:%Y-%m-%d-%H:%M:%S}-{}".format(
            datetime.datetime.now(),
            uuid.uuid4())
        self.path = executionRoot/self.name
        self._pid = None

    def createSandbox(self):
        self.path.mkdir()

    def run(self, command):
        output = self.outputFile.open('w')
        process = subprocess.Popen(
            command,
            cwd=str(self.path),
            stdout=output,
            stderr=output,
        )
        self.pidFile.write_text('{}'.format(process.pid))
        return process

    @property
    def outputFile(self):
        return self.path / 'output.txt'

    @property
    def pidFile(self):
        return self.path / 'pid'

    @property
    def pid(self):
        if self._pid:
            return self._pid
        if not self.pidFile.exists():
            return None
        self._pid = int(self.pidFile.read_text())
        return self._pid

    def stop(self):
        if not self.pid: return False
        try:
            os.kill(self.pid, signal.SIGINT)
        except OSError as err:
            if err.errno == errno.ESRCH: # Process not found
                return False
            raise # EPERM or any other
        return True

    def kill(self):
        if not self.pid: return False
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError as err:
            if err.errno == errno.ESRCH: # Process not found
                return False
            raise # EPERM or any other
        return True

    def remove(self):
        if not self.pid: return False
        if self.isAlive: return False
        removeRecursive(self.path)
        return True

    def isRunning(self):
        if self.pid: return True
        return False

    # TODO: TEST
    @property
    def isAlive(self):
        import psutil
        if not psutil.pid_exists(self.pid):
            return False
        status = psutil.Process(self.pid).status()
        if status == psutil.STATUS_ZOMBIE:
            return False
        if status == psutil.STATUS_DEAD:
            return False
        return True

    # TODO: TEST
    @property
    def state(self):
        if self.pid is None: return 'Launching'
        if self.isAlive: return 'Running'
        return 'Stopped'

    # TODO: TEST
    def listInfo(self):
        return ns(
            name = self.name,
            killDisplay = 'inline' if self.state == 'Running' else 'none',
            removeDisplay = 'inline' if self.state == 'Stopped' else 'none',
            state = self.state,
            )

    # TODO: TEST
    @staticmethod
    def ensureRootExists():
        executionRoot.mkdir(exist_ok=True)

from slugify import slugify

class PlannerExecution(Execution):

    def __init__(self, monday, configPath,
            description='',
            nlines=7,
            ):
        self.nlines = nlines
        name = monday
        if description:
            name = "{}-{}".format(monday, slugify(description))
        super(PlannerExecution, self).__init__(name=name)
        self.configPath = Path(configPath)

    def createSandbox(self):
        super(PlannerExecution, self).createSandbox()
        config = ns.load(self.configPath/'config.yaml')
        config.nTelefons = self.nlines
        config.dump(self.path/'config.yaml')
        (self.path/'holidays.conf').write_bytes(
            (self.configPath/'holidays.conf').read_bytes()
            )
        (self.path/'drive-certificate.json').symlink_to(
            (self.configPath/'drive-certificate.json').resolve())


# TODO: Testing del sandbox



# vim: ts=4 sw=4 et
