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
from tomatic.retriever import (
    downloadPersons,
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
class Config:

    def __init__(self, config_file, date = None, keep = False):
        step('Carregant configuració {}...', config_file)
        try:
            self.data = ns.load(config_file)
            self._update_monday(date)
            not keep and downloadPersons(self.data)
            self._update_persons()
            if not self.data.get('idealshifts'):
                self.data.idealshifts = 'idealshifts.yaml'
                not keep and downloadIdealLoad(self.data, args.certificate)
            if not self.data.get('weekShifts') and not self.data.computeShifts:
                self.data.weekShifts = 'carrega.csv'
                not keep and downloadShiftload(self.data)
            if not self.data.computeShifts:
                self.data.overloadfile = "overload-{}.yaml".format(self.data.monday)
                not keep and downloadOverload(self.data)
            not keep and self._download_leaves()
            if not self.data.get('busyFiles'):
                not keep and self._download_busy()
            if self.data.computeShifts:
                self.update_shifts()
        except:
            error("Configuració incorrecta")
            raise

    def update_shifts(self):
        setup = ShiftLoadComputer.loadData(self.data)
        self.data.idealLoad = setup.idealLoad
        self.data.busyTable = setup.busyTable._table

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

    def _download_leaves(self):
        self.data.driveCertificate = args.certificate
        downloadLeaves(self.data, args.certificate)

    def _download_busy(self):
        downloadBusy(self.data)
        downloadFestivities(self.data)
        downloadVacations(self.data, source=args.holidays)

    def set_ignore_optionals(self, ignore = False):
        self.data.ignoreOptionalAbsences = ignore



class Menu:

    def __init__(self, config):
        self.nPersones = len(config.idealLoad)
        self.nLinies = config.nTelefons
        self.nSlots = len(config.hours) - 1
        self.nNingus = config.nNingusMinizinc
        self.nDies = len(config.diesCerca)
        self.maxTorns = config.maximHoresDiariesGeneral
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
        for solution2 in solution.solution.ocupacioSlot:
            for sol in solution2:
                print(f"({len(sol)}):   ", [self.names[s - 1] for s in sol])
            print("\n")
        return solution2


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
    config = Config(args.config_file, args.date, args.keep)
    # Fist try to get a solution with optional absences
    step('Provant amb les indisponibilitats opcionals...')
    # choose a list of minizinc solvers to user
    solvers = ["chuffed", "coin-bc"]
    solution = solve_problem(config.data, solvers)
    if not solution:
        step('Sense solució.\nProvant sense les opcionals...')
        # Ignore optional absences
        config.set_ignore_optionals(True)
        # Update scenario without optional absences
        config.update_shifts()
        solution = solve_problem(config.data, solvers)

    print("Translated solution :D\n", solution)