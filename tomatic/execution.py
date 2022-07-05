# -*- coding: utf-8 -*-

"""
TODO:
- Exit code
"""
import requests
import os
import signal
import errno
import subprocess
import uuid
import datetime
from pathlib import Path
from consolemsg import step, success, warn, error, u
from yamlns import namespace as ns
from . import schedulestorage

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

    @classmethod
    def list(cls):
        return [
            cls(p.name) for p in reversed(sorted(
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
        if self.isRunning: return False
        removeRecursive(self.path)
        return True

    @property
    def startTime(self):
        if not self.path.exists(): return None
        return datetime.datetime.utcfromtimestamp(self.path.stat().st_ctime)

    @property
    def isRunning(self):
        import psutil
        if not self.pid: return False
        if not psutil.pid_exists(self.pid): return False
        status = psutil.Process(self.pid).status()
        if status == psutil.STATUS_ZOMBIE:
            return False
        # TODO: Untested condition
        if status == psutil.STATUS_DEAD:
            warn("Untested condition: process STATUS_DEAD")
            return False
        return True

    def listInfo(self):
        return ns(
            name = self.name,
            state = self.state,
            startTime = self.startTime,
            )

    # TODO: TEST
    @property
    def state(self):
        if self.pid is None: return 'Launching'
        if self.isRunning: return 'Running'
        return 'Stopped'

    # TODO: TEST
    @staticmethod
    def ensureRootExists():
        executionRoot.mkdir(exist_ok=True)

from slugify import slugify

class PlannerExecution(Execution):

    def __init__(self,
            name=None,
            monday=None,
            configPath=None,
            description='',
            nlines=7,
            ):
        if not name:
            name = monday
            if description:
                name = "{}-{}".format(monday, slugify(description))
        else:
            monday = name[:len('YYYY-MM-DD')]
            description = name[len('YYYY-MM-DD-'):]

        super(PlannerExecution, self).__init__(name=name)

        self.monday = monday
        self.description = description
        self.nlines = nlines

        # TODO: configless not tested
        self.configPath = Path(configPath or '.')

    def createSandbox(self):
        super(PlannerExecution, self).createSandbox()
        config = ns.load(self.configPath/'config.yaml')
        config.nTelefons = self.nlines
        config.maxOverload = 0
        config.dump(self.path/'config.yaml')
        (self.path/'holidays.conf').write_bytes(
            (self.configPath/'holidays.conf').read_bytes()
            )
        (self.path/'drive-certificate.json').symlink_to(
            (self.configPath/'drive-certificate.json').resolve())

    def listInfo(self):
        info = ns(
                super(PlannerExecution, self).listInfo(),
                totalCells=None,
                completedCells=None,
                solutionCost=None,
                timeOfLastSolution=None,
                unfilledCell=None,
                busyReasons={},
            )
        try:
            specific = ns.load(self.path/'status.yaml')
        except IOError as e:
            return info

        info.update(specific)
        info.timeOfLastSolution = datetime.datetime.strptime(info.timeOfLastSolution,'%Y-%m-%d %H:%M:%S.%f')
        return info
            

    # TODO: TEST
    @staticmethod
    def start(monday, description, **kwds):
        execution = PlannerExecution(
            monday=monday,
            description=description or u(uuid.uuid4()),
            nlines=kwds.get('nlines'),
            configPath=Path('.'),
        )
        execution.createSandbox()
        step("Running {}...", execution.name)
        process = execution.run([
            str(Path('./scripts/tomatic_scheduler.py').resolve()),
            monday or nextMonday(),
        ])
        step("Process {}...", execution.pid)
        children[process.pid] = process
        return execution.name

    @property
    def solutionHtml(self):
        return self.path/'graella-telefons-{}.html'.format(self.monday)

    @property
    def solutionYaml(self):
        return self.path/'graella-telefons-{}.yaml'.format(self.monday)

    # TODO: TEST
    def upload(self, uploader):
        schedules = schedulestorage.Storage.default()
        timetable = ns.load(self.solutionYaml)
        logmsg = (
            "{}: {} ha pujat {} ".format(
            datetime.datetime.now(),
            uploader,
            timetable.week,
            ))
        timetable.setdefault('log',[]).append(logmsg)
        schedules.save(timetable)
        schedulestorage.publishStatic(timetable)

# TODO: Unify other implementations
# TODO: TEST
def nextMonday(today=None):
    today = today or datetime.date.today()
    nextWeek = today + datetime.timedelta(days=7)
    return u(nextWeek - datetime.timedelta(days=today.weekday()))

"""
TODO's:
- [x] Default description uses uuid
- [x] Scheduler should dump status.yaml
- [x] No cache for output and result
- [x] Kill Action
- [x] Upload Action
- [x] Output Ansi codes -> html
- [x] Move spike to tomatic
- [x] Correct relative paths to scheduler script
- [x] Correct relative paths to config path
- [x] Correct redirections and links
- [x] Show the blocking cell for humans (ie dl 10:15 L7)
- [ ] Fix: Output when no output yet -> 500
- [ ] Output html should contain overloads and penalties
- [ ] Handle sandbox already exists (same non-empty description)
"""



# vim: ts=4 sw=4 et
