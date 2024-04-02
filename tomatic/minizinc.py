import asyncio
from tomato_cooker.models import TimetableProblem
from consolemsg import step, error, success
from yamlns import namespace as ns
import random
import datetime
from .scenario_config import Config
from .htmlgen import HtmlGen
from .busy import laborableWeekDays
from pathlib import Path

class Minizinc:

    NOBODY = 'ningu'
    FESTIVITY = 'festiu'
    NORMAL_WEEKDAYS = 'dl dm dx dj dv'.split()

    def __init__(self, config):
        self.config = config
        self.days = laborableWeekDays(config.monday)
        self.WEEKDAY = { day: i for i, day in enumerate(self.days) }
        self.deterministic = config.get('deterministic', False)

        # choose a list of minizinc solvers to user
        solvers = config.minizincSolvers # TODO: no op now

        persons = list(sorted(config.finalLoad.keys()))
        if self.NOBODY not in persons:
            persons.append(self.NOBODY)
        if not self.deterministic:
                random.shuffle(persons)
        finalLoad = [config.finalLoad.get(p,0) for p in persons]

        self.problem = TimetableProblem(
            names = persons,
            Nobodies = [self.NOBODY],
            maxLoad = finalLoad,
            days = self.days,
            maxPersonLoadPerDay = config.maximHoresDiariesGeneral,
            nHours = len(config.hours) - 1,
            nLines = config.nTelefons,
        )
        self._fillFixed(config)
        self._fillBusyAndUndesired(config)
        self.overload = ns.load(self.config.overloadfile)

    def _fillFixed(self, config):
        for ((day, hour, line), person) in config.get('forced',{}).items():
            if day not in self.problem.days: continue
            if day not in self.WEEKDAY: continue
            if person not in self.problem.names: continue
            iday = self.WEEKDAY[day]
            self.problem.forced[iday][hour].add(person)

    def _fillBusyAndUndesired(self, config) :

        self.undesiredReasons = dict()
        self.busyReasons = dict()

        from .busy import busyIterator
        for day, ihour, person, optional, reason in busyIterator(
            config.busyFiles,
            config.monday,
        ):
            if person not in self.problem.names: continue
            if ihour >= self.problem.nHours: continue
            iday = self.WEEKDAY[day]
            if optional:
                self.undesiredReasons[(day,ihour,person)] = reason
                self.problem.undesired[iday][ihour].add(person)
            else:
                self.busyReasons[(day,ihour,person)] = reason
                self.problem.busy[iday][ihour].add(person)

    def compute(self):
        return asyncio.run(
            self.problem.solve(deterministic=self.config.deterministic)
        )

    def _solutionTimetable(self, solution):
        timetable = {
            day: [
                [
                    self.NOBODY if day in self.days else self.FESTIVITY
                    for _ in range(self.problem.nLines)
                ] for _ in range(self.problem.nHours)
            ] for day in self.NORMAL_WEEKDAYS
        }

        for day, hours in zip(self.days, solution.timetable):
            for hour_i, hour in enumerate(hours):
                for line_i, person in enumerate(sorted(hour, key=lambda x: 'zzz' if x==self.NOBODY else x )):
                    timetable[day][hour_i][line_i] = person
        return timetable

    def _solutionPenalties(self, solution):
        penaltyProcessors = dict(
            emptySlots = lambda day, hour, blanks: (
                self.problem.penaltyEmpty*blanks*blanks,
                f"{blanks} forats a {day} {self.config.hours[hour-1]} ",
            ),
            unforced = lambda day, hour, person: (
                self.problem.penaltyUnforced,
                f"{day} {self.config.hours[hour-1]} "
                f"Torn fix no col·locat de {person}",
            ),
            undesiredPenalties = lambda day, hour, person: (
                self.problem.penaltyUndesiredHours,
                f"{person} {day} {self.config.hours[hour-1]} "
                f"no li va be per: "
                f"{self.undesiredReasons[(day,hour-1,person)]}",
            ),
            concentratedLoad = lambda day, person, nhours: (
                self.problem.penaltyMultipleHours*nhours*(nhours-1),
                f"{person} {day} té {nhours} hores el mateix dia",
            ),
            discontinuousPenalties = lambda day, person: (
                self.problem.penaltyDiscontinuousHours,
                f"{person} {day} té torns intercalats",
            ),
            farDiscontinuousPenalties = lambda day, person: (
                self.problem.penaltyFarDiscontinuousHours,
                f"{person} {day} té torns intercalats (als extrems)",
            ),
            marathonPenalties = lambda day, person: (
                self.problem.penaltyMarathon,
                f"{person} {day} té 3 hores sense descans",
            ),
            noBrunchPenalties = lambda day, person: (
                self.problem.penaltyNoBrunch,
                f"{person} {day} no pot esmorzar"
            ),
        )

        return [
            processor(*penalty)
            for kind, processor in penaltyProcessors.items()
            for penalty in getattr(solution, kind)
        ]


    def translateSolution(self, mzresult):
        # Print Minizinc output
        print("Solucio:\n")
        print(mzresult)

        solution = mzresult.solution

        result = ns(
            week=f'{self.config.monday}',
            days=self.NORMAL_WEEKDAYS,
            hours=self.config.hours,
            turns=[ f"L{line+1}" for line in range(self.config.nTelefons) ],
            timetable=self._solutionTimetable(solution),
            colors=self.config.colors,
            extensions=self.config.extensions,
            names=self.config.names,
            overload = self.overload,
            penalties = self._solutionPenalties(solution),
            cost = solution.cost,
            log=[], # Starts empty
        )
        return result



def main(args):
    config = Config(**vars(args))
    target_date = args.date or config.data.monday
    output_yaml = "graella-telefons-{}.yaml".format(config.data.monday)
    output_html = "graella-telefons-{}.html".format(config.data.monday)
    status_file = "status.yaml"

    step('Llençant MiniZinc...')
    minizinc = Minizinc(config.data)
    results = minizinc.compute()
    solution = minizinc.translateSolution(results)

    if not solution:
        error("No s'ha trobat resultat... :(")
        return False

    success("Resultat desat a {}", output_yaml)
    solution.dump(output_yaml)
    success("Resultat desat a {}", output_html)
    Path(output_html).write_text(HtmlGen(solution).html())

    totalCells=len(minizinc.days)*(len(solution.hours)-1)*len(solution.turns)
    completedCells=results.solution.completion
    ns(
        totalCells=totalCells,
        completedCells=completedCells,
        solutionCost=solution.cost,
        timeOfLastSolution=f'{datetime.datetime.utcnow()}',
        unfilledCell='Complete' if totalCells == completedCells else 'Partial',
        busyReasons={},
        penalties=solution.penalties,
    ).dump(status_file)
    return True


