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

    def __init__(self,
        config_file,
        date,
        keep,
        certificate,
        holidays,
        lines=None,
        deterministic=False,
        verbose=None,
        track=None,
        personsfile=None,
        compute_shifts=None,
        drive_file=None,
        idealshifts=None,
        weekshifts=None,
        overload=None,
        forgive=None,
        clusterize=None,
        search_days=None,
        stop_penalty=None,
        summary=None,
        **kwds
    ):
        step('Carregant configuració {}...', config_file)
        try:
            self.data = ns.load(config_file)
            config = self.data
        except Exception as e:
            error("Error llegint {}: {}", config_file, e)
            raise
        try:

            config.verbose = verbose if verbose else []
            if track:
                config.mostraCami = True

            self.data.forgive = forgive if forgive is not None else confgi.get('forgive', False)
            self.data.clusterize = clusterize if clusterize is not None else confgi.get('clusterize', False)
            self.data.summary = summary
            # specific of backtracker
            if deterministic:
                self.data.aleatori = not deterministic
            self.data.deterministic = not self.data.get('aleatori', True)

            # specific of backtracker
            if search_days:
                config.diesCerca = search_days.split(',')

            # specific of backtracker
            if stop_penalty:
                config.stopPenalty = stop_penalty


            # Configure persons
            config.personsfile = personsfile or config.get('personsfile', 'persons.yaml')
            if not personsfile and not keep:
                downloadPersons(config)
            from .persons import persons
            config.update(persons(config.personsfile))

            self._update_monday(date)

            if lines is not None:
                self.data.nTelefons = lines

            if drive_file:
                config.documentDrive = drive_file

            config.computeShifts = config.get('computeShifts') or compute_shifts

            mustDownloadIdealShifts = not idealshifts and not config.get('idealshifts')
            config.idealshifts = idealshifts or config.get('idealshifts') or 'idealshifts.yaml'

            if not keep:
                self._download_leaves(certificate)

            if not keep and mustDownloadIdealShifts:
                downloadIdealLoad(self.data, certificate)

            # TODO: Not for shiftload
            mustDownloadShifts = not weekshifts and not config.get('weekShifts') and not config.computeShifts
            config.weekShifts = config.get('weekShifts') or weekshifts or 'carrega.csv'
            if not keep and mustDownloadShifts:
                downloadShiftload(self.data)

            # TODO: Not in shiftload.py
            mustDownloadOverload = not overload and not config.computeShifts
            config.overloadfile = overload or "overload-{}.yaml".format(config.monday)
            if not keep and mustDownloadOverload:
                downloadOverload(config)

            if not keep and not self.data.get('busyFiles'):
                self._download_busy(holidays)

            # TODO: shiftload.py does it inconditional
            if self.data.get("computeShifts"):
                if not keep:
                    step("Baixant bossa d'hores del tomatic...")
                    downloadShiftCredit(self.data)
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
            forgive = config.forgive,
            inclusters = config.clusterize,
        )
        # TODO: Take it from proper source
        args = ns(
            weekshifts=config.weekShifts,
            overload=config.overloadfile,
            summary=config.summary,
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
