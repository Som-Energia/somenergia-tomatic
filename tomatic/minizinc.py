import asyncio
from tomato_cooker.grill import GrillTomatoCooker
from tomato_cooker.models import TomaticProblem, tomatic
from consolemsg import step, error, success
from yamlns import namespace as ns
import random
import datetime
from .backtracker import parseArgs
from .scenario_config import Config
from .htmlgen import HtmlGen
from .busy import laborableWeekDays


class Menu:

    NINGU = 'ningu'
    NORMAL_WEEKDAY = {
        'dl': 0,
        'dm': 1,
        'dx': 2,
        'dj': 3,
        'dv': 4,
    }

    def __init__(self, config):
        laborable_days = laborableWeekDays(config.monday)
        self.nPersones = len(config.finalLoad)
        self.nLinies = config.nTelefons
        self.nSlots = len(config.hours) - 1
        self.nNingus = config.nNingusMinizinc
        self.nDies = len(laborable_days)
        self.maxTorns = config.maximHoresDiariesGeneral
        self._saveNamesAndTurns(config.finalLoad)
        self.laborable_days = laborable_days
        self.WEEKDAY = { day: i for i, day in enumerate(laborable_days) }
        self.indisponibilitats = self._indisponibilities(config)
        self.forcedTurns = self._forcedTurns(config)

    def _saveNamesAndTurns(self, fulls):
        persons = list(fulls.keys())
        random.shuffle(persons)
        shuffled_fulls = [(key, fulls[key]) for key in persons]
        names, turns = zip(*shuffled_fulls)
        self.nTorns  = list(turns)
        self.names = list(names)

    def _indisponibilities(self, config):
        persons_indisponibilities = {
            name: [set() for _ in range(self.nDies)] for name in self.names
        }
        for day, turn, name in config.busyTable:
            if config.busyTable[(day, turn, name)] and day in self.laborable_days:
                persons_indisponibilities[name][self.WEEKDAY[day]].add(turn + 1)
        indisponibilities = []
        for name in self.names:
            indisponibilities.extend(persons_indisponibilities[name])
        return indisponibilities

    def _forcedTurns(self, config):
        forcedTurns = [set() for _ in range(self.nPersones * self.nDies)]
        for ((day, hour, line), person) in config.get('forced',{}).items():
            if day not in self.laborable_days: continue
            if person not in self.names: continue

            iday = self.laborable_days.index(day)
            iperson = self.names.index(person)
            idx = iperson * self.nDies + iday
            forcedTurns[idx].add(hour+1)
        return forcedTurns

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
            forcedTurns=self.forcedTurns
        )

    def translate(self, solution, config):
        days = list(self.NORMAL_WEEKDAY.keys())
        timetable = {
            day: [
                [
                    self.NINGU for _ in range(self.nLinies)
                ] for _ in range(self.nSlots)
            ] for day in days
        }

        for day, turns in zip(self.laborable_days, solution.solution.ocupacioSlot):
            for turn_i, turn in enumerate(turns):
                for slot_i, person in enumerate(turn):
                    timetable[day][turn_i][slot_i] = self.names[person-1]

        result = ns(
            week=f'{config.monday}',
            days=days,
            hours=config.hours,
            turns=[ f"T{torn+1}" for torn in range(config.nTelefons) ],
            timetable=timetable,
            colors=config.colors,
            extensions=config.extensions,
            names=config.names,
            overload={},  # empty here
            penalties=[],  # empty here
            cost=solution.solution.totalTorns,
            log=[]  # TODO: empty?
        )
        return result


def make_html_file(solution, filename):
    html_gen = HtmlGen(solution)
    with open(filename, 'w') as file:
        file.write(
            html_gen.htmlHeader() +
            html_gen.htmlColors() +
            html_gen.htmlSubHeader() +
            html_gen.htmlSetmana() +
            html_gen.htmlTable()+
            html_gen.htmlPenalties()+
            html_gen.htmlExtensions()+
            html_gen.htmlFooter()
        )


def solve_problem(config, solvers):
    menu = Menu(config)
    # define a problem
    tomatic_problem_params = menu.ingredients()
    tomatic_problem = TomaticProblem(**tomatic_problem_params)
    # create an instance of the cooker
    tomato_cooker = GrillTomatoCooker(tomatic.MODEL_DEFINITION_PATH, solvers)
    # Now, we can solve the problem
    solution = asyncio.run(tomato_cooker.cook(tomatic_problem))
    return menu.translate(solution, config) if solution else False


def main():
    args = parseArgs()
    config = Config(
        args.config_file,
        args.date,
        args.keep,
        args.certificate,
        args.holidays
    )
    # TODO: check where to save this
    target_date = args.date or config.data.monday
    output_yaml = "graella-telefons-{}.yaml".format(target_date)
    output_html = "graella-telefons-{}.html".format(target_date)
    status_file = "status.yaml"
    # Fist try to get a solution with optional absences
    step('Provant amb les indisponibilitats opcionals...')
    # choose a list of minizinc solvers to user
    solvers = config.data.minizincSolvers
    solution = solve_problem(config.data, solvers)
    if not solution:
        step('Sense solució.\nProvant sense les opcionals...')
        # Ignore optional absences
        config.set_ignore_optionals(True)
        # Update scenario without optional absences
        config.update_shifts()
        solution = solve_problem(config.data, solvers)
    # Save reslut if result else say there is no result
    if solution:
        solution.dump(output_yaml)
        make_html_file(solution, output_html)
        success("Resultat desat a {}", output_yaml)
        success("Resultat desat a {}", output_html)
        # TODO: try to not do this 🥺
        ns(
            totalCells=-1,
            completedCells=-1,
            solutionCost=0,
            timeOfLastSolution=f'{datetime.datetime.now()}',
            unfilledCell='Complete',
            busyReasons={},
            penalties=[]
        ).dump(status_file)
        return True

    error("No s'ha trobat resultat... :(")
    return False
