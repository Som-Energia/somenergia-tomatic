import asyncio
from tomato_cooker.grill import GrillTomatoCooker
from tomato_cooker.models import TomaticProblem, tomatic
from consolemsg import step, error
from yamlns import namespace as ns
import datetime
import random
from .retriever import addDays
from .shiftload import ShiftLoadComputer
from .backtracker import parseArgs
from .persons import persons
from tomatic.retriever import (
    downloadLeaves,
    downloadIdealLoad,
    downloadVacations,
    downloadFestivities,
    downloadBusy,
    downloadShiftload,
    downloadOverload,
    addDays,
)

WEEKDAY = {
    'dl': 0,
    'dm': 1,
    'dx': 2,
    'dj': 3,
    'dv': 4,
}

# TODO: extract this
def update_config(config):
    config.update(persons(config.get('personsfile', None)))
    # TODO: We should have the option to specity other mondays
    today = datetime.date.today()
    config.monday = addDays(today, 7 - today.weekday())
    # TODO: Removed the download files, check side effects
    mustDownloadIdealShifts = not config.get('idealshifts')
    config.idealshifts = config.get('idealshifts') or 'idealshifts.yaml'
    mustDownloadShifts = not config.computeShifts
    config.weekShifts = config.get('weekShifts') or 'carrega.csv'
    mustDownloadOverload = not config.computeShifts
    config.overloadfile = "overload-{}.yaml".format(config.monday)
    step("Baixant persones de baixa del drive...")
    config.driveCertificate = args.certificate
    downloadLeaves(config, args.certificate)
    if mustDownloadIdealShifts:
        downloadIdealLoad(config, args.certificate)
    if mustDownloadShifts:
        downloadShiftload(config)
    if mustDownloadOverload:
        downloadOverload(config)
    if not config.get('busyFiles'):
        downloadBusy(config)
        downloadFestivities(config)
        downloadVacations(config, source=args.holidays)
    if config.computeShifts:
        setup = ShiftLoadComputer.loadData(config)
        config.idealLoad = setup.idealLoad
        config.busyTable = setup.busyTable._table


class Menu:

    def __init__(self, config):
        self.nPersones = len(config.idealLoad)
        self.nLinies = config.nTelefons
        self.nSlots = len(config.hours) - 1
        self.nNingus = config.nNingusMinizinc
        self.nDies = len(config.diesCerca)
        self.maxTorns = config.maximHoresDiariesGeneral
        # TODO: create a method to shuffle this
        self._saveNamesAndTurns(config.idealLoad)
        self.indisponibilitats = self._indisponibilities(config)

    def _saveNamesAndTurns(self, ideals):
        persons = list(ideals.keys())
        random.shuffle(persons)
        shuffled_ideals = [(key, ideals[key]) for key in persons]
        names, turns = zip(*shuffled_ideals)
        self.nTorns = list(turns)
        self.names = list(names)

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
                print(f"({len(sol)}):   ", [self.names[s - 1] for s in sol])
            print("\n")
        return solution


def solve_problem(config, solvers):
    menu = Menu(config)
    # define a problem
    tomatic_problem_params = menu.ingredients()
    tomatic_problem = TomaticProblem(**tomatic_problem_params)
    # create an instance of the cooker
    tomato_cooker = GrillTomatoCooker(tomatic.MODEL_DEFINITION_PATH, solvers)
    # Now, we can solve the problem
    solution = asyncio.run(tomato_cooker.cook(tomatic_problem))
    print(solution)
    return menu.translate(solution) if solution else False


def main():
    global args
    args = parseArgs()
    step('Carregant configuració {}...', args.config_file)
    try:
        config = ns.load(args.config_file)
    except:
        error("Configuració incorrecta")
        raise
    # Fist try to get a solution with optional absences
    step('Provant amb les indisponibilitats opcionals...')
    config.ignoreOptionalAbsences = False
    update_config(config)
    # choose a list of minizinc solvers to user
    solvers = ["chuffed", "coin-bc"]
    solution = solve_problem(config, solvers)
    if not solution:
        step('Sense solució.\nProvant sense les opcionals...')
        # Ignore optional absences
        config.ignoreOptionalAbsences = True
        update_config(config)  # TODO: not download everything
        solution = solve_problem(config, solvers)

    print("Translated solution :D\n", solution)