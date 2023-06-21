from consolemsg import step, error, warn
from yamlns import namespace as ns
import datetime
from .retriever import addDays
from .shiftload import ShiftLoadComputer
from .scheduling import timetable2forced
from tomatic.retriever import (
    downloadPersons,
    downloadLeaves,
    downloadIdealLoad,
    downloadVacations,
    downloadFestivities,
    downloadBusy,
    downloadShiftload,
    downloadOverload,
    downloadShiftCredit,
    addDays,
)


class Config:

    def __init__(self, config_file, date, keep, certificate, holidays, nLines=None, deterministic=False):
        step('Carregant configuració {}...', config_file)
        try:
            self.data = ns.load(config_file)
        except Exception as e:
            error("Error llegint {}: {}", config_file, e)
            raise
        try:
            self.data.deterministic = deterministic
            if nLines is not None:
                self.data.nTelefons = nLines
            self._update_monday(date)
            not keep and downloadPersons(self.data)
            self._update_persons()
            if not self.data.get('idealshifts'):
                self.data.idealshifts = 'idealshifts.yaml'
                not keep and downloadIdealLoad(self.data, certificate)
            if not self.data.get('weekShifts') and not self.data.get("computeShifts"):
                self.data.weekShifts = 'carrega.csv'
                not keep and downloadShiftload(self.data)
            if not self.data.get("computeShifts"):
                self.data.overloadfile = "overload-{}.yaml".format(self.data.monday)
                not keep and downloadOverload(self.data)
            not keep and self._download_leaves(certificate)
            if not self.data.get('busyFiles'):
                not keep and self._download_busy(holidays)
            if self.data.get("computeShifts"):
                not keep and step("Baixant bossa d'hores del tomatic...")
                not keep and downloadShiftCredit(self.data)
                self.update_shifts()
            if self.data.get('forcedTimeTable'):
                step(f"Lodading forced turns from {self.data.get('forcedTimeTable')}...")
                forcedTimeTable = ns.load(self.data.get('forcedTimeTable'))
                self.data.forced = timetable2forced(forcedTimeTable.timetable)
            else:
                warn("No forcedTimeTable configured")
        except Exception as e:
            error("{}", e)
            raise

    def update_shifts(self):
        config = self.data
        setup = ShiftLoadComputer.loadData(config)
        computer = ShiftLoadComputer(
            nlines = config.nTelefons,
            generalMaxPerDay = config.maximHoresDiariesGeneral,
            maxPerDay = config.maximHoresDiaries,
            maxOverload = config.maxOverload,
            leaves = setup.leaves,
            daysoff = setup.daysoff,
            busyTable = setup.busyTable,
            businessDays = setup.businessDays,
            idealLoad = setup.idealLoad,
            credits = setup.formerCredit,
            monday = config.monday,
            forgive = config.get('forgive', False), # TODO: Pass forgive from args to config
            inclusters = config.get('clusterize', False), #TODO: Pass clusterize from args to config
        )
        args = ns(
            weekshifts='carrega.yaml',
            overload='overload.yaml',
            summary=None,
        )
        computer.outputResults(args)

        # When 'ningu' has more load than turns exist, just adjust the lines
        nHours = len(config.hours) - 1
        nTurns = len(setup.businessDays) *  nHours
        nUncoverdLines, nEmptySlots = divmod(computer.final.get('ningu', 0), nTurns)

        config.finalLoad = ns(
            computer.final,
            ningu=nEmptySlots,
        )
        config.busyTable = setup.busyTable._table
        config.nTelefons -= nUncoverdLines

    def _update_persons(self):
        from .persons import persons
        self.data.update(persons(self.data.get('personsfile', None)))

    def _update_monday(self, date):
        if date is not None:
            # take the monday of the week including that date
            givenDate = datetime.datetime.strptime(date,"%Y-%m-%d").date()
            self.data.monday = addDays(givenDate, -givenDate.weekday())
        else:
            # If no date provided, take the next monday
            today = datetime.date.today()
            self.data.monday = addDays(today, 7-today.weekday())

    def _download_leaves(self, certificate):
        self.data.driveCertificate = certificate
        downloadLeaves(self.data, certificate)

    def _download_busy(self, holidays):
        downloadBusy(self.data)
        downloadFestivities(self.data)
        downloadVacations(self.data, source=holidays)

    def set_ignore_optionals(self, ignore = False):
        self.data.ignoreOptionalAbsences = ignore