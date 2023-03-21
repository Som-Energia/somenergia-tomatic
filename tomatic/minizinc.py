import asyncio
from tomato_cooker.grill import GrillTomatoCooker
from tomato_cooker.models import TomaticProblem, tomatic
from consolemsg import step, error
from yamlns import namespace as ns
import datetime
from .retriever import (
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

WEEKDAY = {
    'dl': 0,
    'dm': 1,
    'dx': 2,
    'dj': 3,
    'dv': 4,
}

class Menu:

    def __init__(self, config):
        self.nPersones = len(config.idealLoad)
        self.nLinies = config.nTelefons
        self.nSlots = len(config.hours) - 1
        self.nNingus = config.maxNingusPerTurn  # revisar
        self.nDies = len(config.diesCerca)
        self.maxTorns = config.maximHoresDiariesGeneral
        # TODO: create a method to shuffle this
        self.nTorns = list(config.idealLoad.values())
        self.names = list(config.idealLoad.keys())
        # TODO: check this because when a set is empty it crashes
        self.indisponibilitats = self._indisponibilities(config)

    def _indisponibilities(self, config):
        persons_indisponibilities = {
            name: [set()] * self.nDies for name in self.names
        }
        for day, turn, name in config.busyTable:
            if config.busyTable[(day, turn, name)]:
                persons_indisponibilities[name][WEEKDAY[day]].add(turn + 1)

        indisponibilities = []
        for name in self.names:
            indisponibilities.extend(persons_indisponibilities[name])

        return indisponibilities

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

    def translate(self, solution):
        # TODO: format solution to tomatic scheduling format
        print("\n")
        for solution in solution.solution.ocupacioSlot:
            for sol in solution:
                print(f"({len(sol)}):   ", [self.names[s] for s in sol])
            print("\n")
        return solution

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
        setup = ShiftLoadComputer.loadData(config)
        config.idealLoad = setup.idealLoad
        config.busyTable = setup.busyTable._table

    # I'm hungry, I want something to eat
    menu = Menu(config)

    # define a problem
    tomatic_problem_params = menu.ingredients()
    tomatic_problem = TomaticProblem(**tomatic_problem_params)

    # choose a list of minizinc solvers to user
    solvers = ["chuffed", "coin-bc"]

    # create an instance of the cooker
    tomato_cooker = GrillTomatoCooker(tomatic.MODEL_DEFINITION_PATH, solvers)

    # Now, we can solve the problem
    solution = asyncio.run(tomato_cooker.cook(tomatic_problem))

    # Tomatic does not understand the solution
    translated_menu = menu.translate(solution)

    print("Translated solution :D\n", translated_menu)