from .execution import Execution, children
from slugify import slugify
import uuid
import datetime
import sys
from pathlib import Path
from consolemsg import step, u
from yamlns import namespace as ns
from . import schedulestorage


class PlannerExecution(Execution):
    """
    Monitors the sandboxed execution of a timetable planner
    """

    def __init__(self,
            name=None,
            monday=None,
            configPath=None,
            description='',
            nlines=7,
            searchDays='',
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
        self.searchDays = [
            x.strip()
            for x in searchDays.split(',')
            if x.strip()
        ]

        # TODO: configless not tested
        self.configPath = Path(configPath or '.')

    def createSandbox(self):
        super(PlannerExecution, self).createSandbox()
        config = ns.load(self.configPath/'config.yaml')
        config.nTelefons = self.nlines
        config.diesCerca = [
            x for x in self.searchDays 
            if x in config.diesCerca
        ] + [
            x for x in config.diesCerca
            if x not in self.searchDays
        ]
        config.maxOverload = 0

        forcedTurnsFile = self.configPath/'data'/'forced-turns.yaml'
        if forcedTurnsFile.exists():
            config.forcedTimeTable = 'forced-turns.yaml'
            (self.path/'forced-turns.yaml').symlink_to(forcedTurnsFile.resolve())

        noservice_file = self.configPath/'data'/'noservice.conf'
        if noservice_file.exists():
            (self.path/'data').mkdir()
            (self.path/'data'/'noservice.conf').symlink_to(noservice_file.resolve())

        dbconfig_file = self.configPath/'dbconfig.py'
        if dbconfig_file.exists():
            (self.path/'dbconfig.py').symlink_to(dbconfig_file.resolve())

        config.dump(self.path/'config.yaml')

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
            searchDays = kwds.get('searchDays') or '',
            configPath=Path('.'),
        )
        execution.createSandbox()
        step("Running {}...", execution.name)
        process = execution.run([
            sys.executable,
            str(Path('./scripts/tomatic_scheduler.py').resolve()),
            monday or nextMonday(),
            '--clusterize',
            '--scheduler', 'minizinc',
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
        schedules = schedulestorage.Storage()
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

