import asyncio
from tomato_cooker.grill import GrillTomatoCooker
from tomato_cooker.models import TomaticProblem, tomatic
from consolemsg import step, error
from yamlns import namespace as ns
import datetime
from .retriever import (
        downloadPersons,
        downloadLeaves,
        downloadIdealLoad,
        downloadVacations,
        downloadFestivities,
        downloadBusy,
        downloadShiftload,
        downloadShiftCredit,
        downloadOverload,
        addDays,
    )
from .shiftload import ShiftLoadComputer
from .backtracker import parseArgs

class Menu:

    def __init__(self, config):
        self.nPersones = self.__numberOfPersons(config)
        self.nLinies = config.nTelefons
        self.nSlots = len(config.hours)
        self.nNingus = config.maxNingusPerTurn  # revisar
        self.nDies = len(config.diesCerca)
        self.maxTorns = config.maximHoresDiariesGeneral
        self.nTorns = [4, 4, 4, 4, 4]
        # TODO: check this because when a set is empty it crashes
        self.indisponibilitats = [
            {1}, {1}, {1}, {1}, {1},
            {1}, {2}, {1}, {2}, {3},
            {5}, {3}, {5}, {3}, {5},
            {4, 5}, {5}, {5}, {5}, {5},
            {4}, {4, 5}, {4}, {4, 5}, {5},
        ]

    def __numberOfPersons(self, config):
        return 5

    def ingredients(self):
        return dict(
            nPersones=self.nPersones,
            nLinies=self.nLinies,
            nSlots=self.nSlots,
            nNingus=self.nNingus,
            nDies=self.nDies,
            maxTorns=self.maxTorns,
            nTorns=self.nTorns,
            indisponibilitats=self.indisponibilitats,
        )

def main():
    global args
    args = parseArgs()

    step('Carregant configuració {}...', args.config_file)
    try:
        config = ns.load(args.config_file)
    except:
        error("Configuració incorrecta")
        raise

    from .persons import persons
    # WIP: Config must contain the name of personsfile
    config.update(persons(config.get('personsfile', None)))

    # WIP: At this moment, monday is always the next monday
    today = datetime.date.today()
    config.monday = addDays(today, 7-today.weekday())

    # Suggestion: dont check and dowload this info here!
    mustDownloadIdealShifts = not config.get('idealshifts')
    config.idealshifts = config.get('idealshifts') or 'idealshifts.yaml'
    mustDownloadShifts = not config.get('weekShifts') and not config.computeShifts
    config.weekShifts = config.get('weekShifts') or 'carrega.csv'
    mustDownloadOverload = not config.computeShifts
    config.overloadfile = "overload-{}.yaml".format(config.monday)

    if not args.keep:
        step("Baixant persones de baixa del drive...")
        certificate = config.driveCertificate
        downloadLeaves(config, certificate)

        if mustDownloadIdealShifts:
            downloadIdealLoad(config, certificate)
        if mustDownloadShifts:
            downloadShiftload(config)
        if mustDownloadOverload:
            downloadOverload(config)
        if not config.get('busyFiles'):
            downloadBusy(config)
            downloadFestivities(config)
            downloadVacations(config, source=args.holidays)

        if config.computeShifts:
            step("Baixant bossa d'hores del tomatic...")
            downloadShiftCredit(config)

    if config.computeShifts:
        # Note: this setup contains the data we need to parse
        setup = ShiftLoadComputer.loadData(config)
        print("Data we need to parse:", setup)

    # define a problem
    tomatic_problem_params = Menu(config).ingredients()
    tomatic_problem = TomaticProblem(**tomatic_problem_params)

    # choose a list of minizinc solvers to user
    solvers = ["chuffed", "coin-bc"]

    # create an instance of the cooker
    tomato_cooker = GrillTomatoCooker(tomatic.MODEL_DEFINITION_PATH, solvers)

    # Now, we can solve the problem
    solution = asyncio.run(tomato_cooker.cook(tomatic_problem))
    print(solution)