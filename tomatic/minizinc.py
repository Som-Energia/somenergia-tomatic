import asyncio
from tomato_cooker.grill import GrillTomatoCooker
from tomato_cooker.models import TomaticProblem, tomatic
from consolemsg import step, error, success
from yamlns import namespace as ns
import random
from .backtracker import parseArgs
from .scenario_config import Config
from .htmlgen import HtmlGen


class Menu:

    WEEKDAY = {
        'dl': 0,
        'dm': 1,
        'dx': 2,
        'dj': 3,
        'dv': 4,
    }

    def __init__(self, config):
        self.nPersones = len(config.idealLoad)
        self.nLinies = config.nTelefons
        self.nSlots = len(config.hours) - 1
        self.nNingus = config.nNingusMinizinc
        self.nDies = len(config.diesCerca)
        self.maxTorns = config.maximHoresDiariesGeneral
        self._saveNamesAndTurns(config.idealLoad)
        self.indisponibilitats = self._indisponibilities(config)
        self.preferencies = self._preferences()

    def _saveNamesAndTurns(self, ideals):
        persons = list(ideals.keys())
        random.shuffle(persons)
        shuffled_ideals = [(key, ideals[key]) for key in persons]
        names, turns = zip(*shuffled_ideals)
        self.nTorns = list(turns)
        self.names = list(names)

    def _indisponibilities(self, config):
        persons_indisponibilities = {
            name: [set() for _ in range(self.nDies)] for name in self.names
        }
        for day, turn, name in config.busyTable:
            if config.busyTable[(day, turn, name)]:
                persons_indisponibilities[name][self.WEEKDAY[day]].add(turn + 1)
        indisponibilities = []
        for name in self.names:
            indisponibilities.extend(persons_indisponibilities[name])
        return indisponibilities

    # TODO: Read preferences from 🕳️
    def _preferences(self):
        preferences = [set() for _ in range(self.nPersones * self.nDies)]
        return preferences

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
            preferencies=self.preferencies
        )

    def translate(self, solution, config):
        days = list(self.WEEKDAY.keys())
        timetable = {
            day: [
              [self.names[person-1] for person in slot] for slot in turn
            ]
            for day, turn in zip(days, solution.solution.ocupacioSlot)
        }
        result = ns(
            week=config.monday,
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
    global args
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
    output_yaml = "graelles/graella-{}.yaml".format(target_date)
    output_html = "graelles/graella-{}.html".format(target_date)
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
    # Save reslut if result else say there is no result
    if solution:
        solution.dump(output_yaml)
        make_html_file(solution, output_html)
        success("Resultat desat a {}", output_yaml)
        success("Resultat desat a {}", output_html)
    else:
        error("No s'ha trobat resultat... :(")
