from consolemsg import step, error, warn
from yamlns import namespace as ns
import datetime
from .shiftload import ShiftLoadComputer
from .scheduling import timetable2forced
from .retriever import (
    downloadPersons,
    downloadLeaves,
    downloadIdealLoad,
    downloadVacations,
    downloadFestivities,
    downloadBusy,
    downloadShiftCredit,
    addDays,
)

def parseArgs():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--keep',
        action='store_true',
        help="no baixa les dades del drive"
        )

    parser.add_argument(
        '--track',
        action='store_true',
        help="visualitza per pantalla el progres de la cerca (molt lent)"
        )

    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        metavar='message',
        nargs='+',
        default=[],
        help="activa els missatges de tall del tipus indicat ('all' per tots)",
        )

    parser.add_argument(
        dest='date',
        nargs='?',
        default=None,
        help='generates the schedule for the week including such date',
        )

    parser.add_argument(
        '--certificate','-C',
        metavar='CERTIFICATE.json',
        default='drive-certificate.json',
        help='certificat amb permisos per accedir al document gdrive',
        )

    parser.add_argument(
        '--scheduler',
        default='backtracker',
        choices='backtracker minizinc'.split(),
        help="search engine for the timetable scheduling",
    )

    parser.add_argument(
        '--holidays',
        default='odoo',
        choices='drive odoo'.split(),
        help="Origen d'on agafa les vacances",
    )

    parser.add_argument(
        '--clusterize',
        action='store_true',
        help="output a line clusterized load",
        )
    parser.add_argument(
        '-l',
        '--lines',
        default=None,
        type=int,
        help="Nombre de linies rebent trucades a la vegada",
    )

    parser.add_argument(
        '--search-days',
        help="dies de cerca per comanda p.e dl,dm,dx,dj,dv sobreescriu config.yaml"
        )

    parser.add_argument(
        '--stop-penalty',
        type=int,
        help="condició de parada al arribar a solució amb la penalització, sobreescriu config.yaml"
        )

    parser.add_argument(
        '--deterministic',
        action='store_true',
        help="desaleatoritza la cerca de branques i possibilitats, sobreescriu config.yaml"
        )

    parser.add_argument(
        '--drive-file',
        help="Document del drive origen de dades externes"
        )

    parser.add_argument(
        '--compute-shifts',
        action='store_true',
        help="Compute the shifts instead of taking the ones in the files"
        )

    parser.add_argument(
        '--config-file',
        default='config.yaml',
        help="fitxer de configuració principal",
    )

    parser.add_argument(
        '--personsfile',
        help="fitxer de configuració de les persones, si s'especifica aqui, no es baixarà",
    )

    parser.add_argument(
        '--idealshifts',
        default=None,
        help="fitxer yaml amb la càrrega ideal de cada persona, si s'especifica aqui no es baixarà",
    )

    parser.add_argument(
        '--weekshifts',
        default=None,
        help="fitxer tsv amb la carrega a cada torn (columna) de cada persona (fila)",
    )

    parser.add_argument(
        '--overload',
        default=None,
        help="fitxer yaml de sortida amb la sobrecàrrega final sobre l'ideal ponderat de cada persona",
    )

    parser.add_argument(
        '--summary',
        default=None,
        help="fitxer tsv amb els detalls de com s'ha anat calculant la càrrega",
    )

    parser.add_argument(
        '--forgive',
        action='store_true',
        help="Deactivate any past debts and credits",
    )

    return parser.parse_args()


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
        scheduler=None,
        summary=None,
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
            self.data.loadSummaryFile = summary
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

            if certificate:
                config.driveCertificate = certificate

            if not keep:
                self._download_leaves()

            mustDownloadIdealShifts = not idealshifts and not config.get('idealshifts')
            config.idealshifts = idealshifts or config.get('idealshifts') or 'idealshifts.yaml'
            if not keep and mustDownloadIdealShifts:
                downloadIdealLoad(self.data)

            config.weekShifts = weekshifts or config.get('weekShifts') or 'carrega.csv'
            config.overloadfile = overload or config.get('overloadfile') or "overload-{}.yaml".format(config.monday)

            if not keep and not self.data.get('busyFiles'):
                self._download_busy(holidays)

            if self.data.computeShifts:
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
        computer.outputResults(config)

        # When 'ningu' has more load than turns exist, just adjust the lines
        nHours = len(config.hours) - 1
        nTurns = len(setup.businessDays) *  nHours
        nUncoverdLines, nEmptySlots = divmod(computer.final.get('ningu', 0), nTurns)
        config.finalLoad = ns(
            computer.final,
            ningu=nEmptySlots,
        )
        config.nTelefons -= nUncoverdLines

        config.busyTable = setup.busyTable._table

    def _update_monday(self, date):
        if date is not None:
            # take the monday of the week including that date
            givenDate = datetime.datetime.strptime(date,"%Y-%m-%d").date()
            self.data.monday = addDays(givenDate, -givenDate.weekday())
        else:
            # If no date provided, take the next monday
            today = datetime.date.today()
            self.data.monday = addDays(today, 7-today.weekday())

    def _download_leaves(self):
        downloadLeaves(self.data)

    def _download_busy(self, holidays):
        downloadBusy(self.data)
        downloadFestivities(self.data)
        downloadVacations(self.data, source=holidays)

    def set_ignore_optionals(self, ignore = False):
        self.data.ignoreOptionalAbsences = ignore
