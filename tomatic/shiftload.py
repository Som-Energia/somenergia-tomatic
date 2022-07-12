#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from pathlib import Path
import datetime

from consolemsg import step, error, warn, success, fail, out, u
from yamlns import namespace as ns

from . import busy


def ponderatedLoad(idealLoad, businessDays, daysoff, leaves):
    """Applies to an ideal load (a dictionary person->load)
    the proportionality of the actual days each person has to
    work removing non business days, days off, and leaves.
    """
    return ns((
        (person, singlePonderatedLoad(
            person=person,
            load=load,
            businessDays = businessDays,
            daysoff = daysoff,
            leaves = leaves,
        ))
        for person, load in idealLoad.items()
    ))

def singlePonderatedLoad(person, load, businessDays, daysoff, leaves):
    """Returns for a given person the ponderated load, that is
    the ideal load for a full week, proportional to the actual working
    days considering businessDays, days off and leavs."""
    return load*workingDays(person, businessDays, daysoff, leaves)/float(5)

def workingDays(person, businessDays, daysoff, leaves):
    """Returns the real working days for a person,
    removing the days off or all if in sick leave.
    """
    if person in leaves: return 0
    ndaysoff = sum(
            day.person == person
            for day in daysoff
            if day.weekday in businessDays
            )
    return len(businessDays)-ndaysoff

def capacity(busytable, generalMaxPerDay, maxPerDay=ns(), leaves=[]):
    """Returns an upper bound to the actual week capacity
    of every person to answer the phone given some constraints
    for working confort and the unavailabilities defined
    in the busy table.
    """
    return ns(
        (person, weekCapacity(
            busy = [
                busytable.showDay(day, person)
                for day in busytable._days
            ],
            maxPerDay = maxPerDay.get(person, generalMaxPerDay),
        ) if person not in leaves else 0)
        for person in busytable._persons
    )


def weekCapacity(busy, maxPerDay):
    """Returns a upper bound for the actual week capacity
    for a person to answer phone given some constraints
    on working confort and the availability of the person.

    @arg maxPerDay is the configured maxPerDay for that person.
    @arg busy is an iterable of strings per day encoding the
        aggregated capacity ['0011', '1010', ... ]
    """
    return sum(dayCapacity(b, maxPerDay) for b in busy)


def dayCapacity(busy, maxPerDay):
    """Returns the upper bound for the actual day capacity
    for a person to answer phone given some constraints
    on working confort and the availability of the person.

    @arg maxPerDay is the configured maxPerDay for that person.
    @arg busy is a string coding shift unavailability for the day
        (one means busy, zero means available)
    """
    # TODO: max=2 but no lunch required
    if busy == '1111': return 0
    if maxPerDay == 1: return 1
    if maxPerDay == 2:
        # Restriction: consecutive and not arround the lunch time, to be two
        if busy[:2] == '00': return 2
        if busy[2:] == '00': return 2
        return 1
    if maxPerDay == 4 and busy=='0000': return 4
    if '000' in busy: return 3
    if '00' in busy: return 2
    return 1


def loadSubstract(minuend, subtrahend):
    """
    Computes the substraction of subtrahend load from minuend load,
    person to person, considering 0 when a person is not
    in a side.
    """
    return ns(
        (person, minuend.get(person, 0) - subtrahend.get(person, 0))
        for person in set(minuend.keys()).union(subtrahend.keys())
    )

def loadSum(*args):
    """
    Computes the addition of all loads passed as arguments,
    person to person, if a person is missing in an argument
    is considered to be 0.
    """
    persons = set().union(*(arg.keys() for arg in args))
    return ns(
        (person, sum(arg.get(person, 0) for arg in args))
        for person in persons
    )

def loadMin(*args):
    """
    Computes the minimum of all loads passed as arguments,
    person to person, if a person is missing in an argument
    is considered to be 0.
    """
    persons = set().union(*(arg.keys() for arg in args))
    return ns(
        (person, min(arg.get(person, 0) for arg in args))
        for person in persons
    )

def loadRound(load):
    """
    Returns a load with the input values rounded
    """
    return ns(
        (p, int(round(v)))
        for p,v in load.items()
    )

def loadDefault(load, persons, value=0):
    return ns(
        (p, load.get(p, value))
        for p in persons
    )

def augmentLoad(load, addend=1):
    """
    Returns a load resulting of adding addend to every person.
    """
    return ns(
        (person, value+addend)
        for person, value in load.items()
    )

def clusterize(nlines, load):
    """
    Distributes persons load on lines so that every line has the
    same total load.
    This distribution makes every person load to be concentrated
    on a single line when feasible.
    This increases cuts of the search space of the backtraking.
    In some situations this distribution could lead to unfeasible
    configurations that could be feasible in a diferent distribution.
    """
    totalLoad = sum(load.values())
    if totalLoad % nlines:
        raise Exception("Total load {} is not divisible by {} lines"
            .format(totalLoad, nlines))
    loadPerLine = totalLoad // nlines
    result = ns(
        (person, [0]*nlines)
        for person in load
    )
    linesTotal = [0]*nlines
    sortedLoads = [
        (person, load)
        for person, load in sorted(load.items(), key=lambda x:-x[1])
        if person != 'ningu'
    ]
    if 'ningu' in load:
        sortedLoads.append(('ningu', load.ningu))

    for person, load in sortedLoads:
        while load:
            lineLoad, line = min((x,i) for i,x in enumerate(linesTotal))
            transferedLoad = min(loadPerLine-lineLoad, load)
            result[person][line]+=transferedLoad
            linesTotal[line]+=transferedLoad
            load-=transferedLoad

    return result

def sortedCreditors(credits, strict=False):
    """
    Generates a sequence of creditors sorted by credit.
    In strict mode, debtors (zero or negative credit) are excluded
    """
    for person, credit in sorted(credits.items(), key=lambda x: (-x[1],x[0])):
        if strict and credit<=0: break
        yield person

def sortedDebtors(credits, strict=False):
    """
    Generates a sequence of debtors sorted by debit (negative credit).
    In strict mode, creditors (zero or positive credit) are excluded
    """
    for person, credit in sorted(credits.items(), key=lambda x: (x[1],x[0])):
        if strict and credit>=0: break
        yield person

def compensateDebtsAndCredits(shifts, credits, limits):
    """
    Exchanges shifts to compensate positive with negative credit
    while keeping shifts positive and under limits.
    """
    result=ns(shifts)
    hasCompensated = True
    while hasCompensated:
        hasCompensated = False
        for debtor, creditor in zip(
                sortedDebtors(credits, strict=True),
                sortedCreditors(credits, strict=True),
                ):
            if result[creditor]<=0: continue
            if result[debtor]>=limits[debtor]: continue
            currentImbalance = abs(credits[debtor]) + abs(credits[creditor])
            proposedImbalance = abs(credits[debtor]+1) + abs(credits[creditor]-1)
            if proposedImbalance >= currentImbalance: continue

            result[debtor] += 1
            credits[debtor] += 1
            result[creditor] -= 1
            credits[creditor] -= 1
            hasCompensated = True
    return result


def achieveFullLoad(fullLoad, shifts, limits, credits):
    """
    Uses current credit (or debit) to make the shift load to be fullLoad.
    Once the credit (or debit) is not usable anymore, it generates
    more debit (or credit) until we have the full load.
    """
    currentLoad = sum(shifts.values())
    if currentLoad > fullLoad:
        return decreaseUntilFullLoad(fullLoad, shifts, limits, credits)
    return increaseUntilFullLoad(fullLoad, shifts, limits, credits)


def decreaseUntilFullLoad(fullLoad, shifts, limits, credits):
    """
    Uses current credit to decrease the current load to reach the full one.
    Once the credit cannot be used anymore, new debit is generated
    to reach it.
    Personal loads are kept zero or positive.
    In each phase persons are selected by decreasing credit one at a time and repeat.
    """
    result = ns(shifts)
    currentLoad = sum(shifts.values())
    operatingWithCredit = True
    while True:
        load = currentLoad
        for person in sortedCreditors(credits, strict=operatingWithCredit):
            if currentLoad == fullLoad: break
            if result[person] <= 0: continue
            credits[person] -= 1
            result[person] -= 1
            currentLoad -= 1
        if load == currentLoad:
            if not operatingWithCredit: break
            operatingWithCredit = False
    return result


def increaseUntilFullLoad(fullLoad, shifts, limits, credits):
    """
    Uses current debit (negative credit) to increase the current load to reach the full one.
    Once the debit cannot be used anymore, new credit is generated
    to reach it.
    Personal limits to the load are respected.
    In each phase persons are selected by decreasing debit (negative credit) one at a time and repeat.
    """
    result = ns(shifts)
    currentLoad = sum(shifts.values())
    operatingWithDebts = True
    while True:
        load = currentLoad
        for person in sortedDebtors(credits, strict=operatingWithDebts):
            if currentLoad == fullLoad: break
            if result[person] >= limits[person]: continue
            credits[person] += 1
            result[person] += 1
            currentLoad += 1
        if load == currentLoad:
            if not operatingWithDebts: break
            operatingWithDebts = False
    return result



class ShiftLoadComputer():

    @staticmethod
    def loadData(config):
        step('Generant càrrega...')
        step("  Carregant dades...")

        step("    Llegint festius...")
        businessDays = busy.laborableWeekDays(config.monday)

        step("    Llegint carrega ideal...")
        idealLoad = ns.load(config.idealshifts)
        persons=list(idealLoad.keys())

        step("    Llegint vacances...")
        daysoffcontent = Path('indisponibilitats-vacances.conf').read_text(encoding='utf8').split("\n")
        daysoff = list(busy.parseBusy(daysoffcontent, error))

        step("    Llegint baixes...")
        leaves = Path('leaves.conf').read_text(encoding='utf8').split()

        step("    Llegint altres indisponibilitats...")
        busyTable = busy.BusyTable(
            days=businessDays,
            nhours=busy.nturns,
            persons=persons,
        )
        busyFiles = config.get('busyFiles', [
            'oneshot.conf',
            'indisponibilitats.conf',
            'indisponibilitats-vacances.conf',
        ])
        for busyfile in busyFiles:
            busyTable.load(busyfile,
                monday = config.monday,
                errorHandler = error,
                justRequired = config.ignoreOptionalAbsences,
            )
        step("    Llegint credits i deutes (bossa d'hores)...")
        formerCredit = ns.load('shiftcredit.yaml')
        return ns(
            monday = config.monday,
            leaves = leaves,
            daysoff = daysoff,
            busyTable = busyTable,
            businessDays = businessDays,
            idealLoad = idealLoad,
            formerCredit = formerCredit,
        )

    def __init__(self,
        nlines,
        generalMaxPerDay,
        maxPerDay,
        leaves,
        daysoff,
        busyTable,
        businessDays,
        idealLoad,
        credits,
        monday,
        forgive=False,
        maxOverload=1,
        inclusters=False,
    ):
        self.monday = monday
        self.nlines = nlines
        self.businessDays = businessDays
        self.idealLoad = idealLoad

        persons=list(idealLoad.keys())

        self.loadedCredit = loadDefault(credits, persons)

        self.initialCredit = self.loadedCredit
        if forgive:
            step("    Ignorant credits i deutes (bossa d'hores)...")
            self.initialCredit = loadDefault(ns(), persons)

        self.credits = ns(self.initialCredit) # copy

        step("  Ponderant la ideal...")
        self.ponderated = ponderatedLoad(
            idealLoad = self.idealLoad,
            businessDays = businessDays,
            daysoff = daysoff,
            leaves = leaves,
        )
        self.rounded = loadRound(self.ponderated)
        nrounded = sum(self.rounded.values())
        success("    Surten {} torns", nrounded)


        step("  Limitant a la capacitat real...")
        self.loadCapacity = capacity(
            busyTable,
            generalMaxPerDay = generalMaxPerDay,
            maxPerDay = maxPerDay,
            leaves = leaves,
        )

        self.augmented = augmentLoad(self.ponderated, addend=maxOverload)
        self.upperBound = loadRound(loadMin(self.augmented, self.loadCapacity))
        self.limited = loadMin(self.rounded, self.upperBound)

        self.reportCapacity()


        self.fullLoad = len(self.businessDays) * busy.nturns * self.nlines
        currentLoad = sum(self.limited.values())
        step("  Completant la carrega de {} a {}...", currentLoad, self.fullLoad)

        self.complete = achieveFullLoad(
            fullLoad = self.fullLoad,
            shifts = self.limited,
            limits = self.upperBound,
            credits = self.credits,
        )
        success("    Carrega assolida {}",sum(self.complete.values()))


        step("  Compensant deute amb credit...")
        self.compensated = compensateDebtsAndCredits(
            shifts = self.complete,
            credits = self.credits,
            limits = self.upperBound,
        )

        self.overload = self.computeOverload()

        self.final = ns((p, int(v)) for p,v in sorted(self.compensated.items()))

        finalLoad = self.finalLoad()
        if finalLoad<self.fullLoad:
            step(f"{finalLoad} torns no arriben als {self.fullLoad} requerits. S'assignent {self.fullLoad-finalLoad} torns, a ningu")
            self.final.ningu = (
                self.final.get('ningu', 0)
                + self.fullLoad
                - finalLoad
            )

        if inclusters:
            self.clusterized = clusterize(self.nlines, self.final)
            self.clusterized.setdefault('ningu', [0]*self.nlines)


    def finalLoad(self):
        return sum(v for k,v in self.final.items())

    def displayOverload(self):
        out("La sobrecarrega d'aquesta setmana seria:")
        for person, value in sorted(self.overload.items(), key=lambda x: x[::-1]):
            if abs(value)<.001: continue
            out("{}: {:.1f}".format(person,value))

    def compensationsSummary(self):
        return '\n'.join(
            "{}: {:.1f}".format(person, value)
            for person, value in loadSubstract(self.compensated, self.complete).items()
            if value)

    def computeOverload(self):
        result = loadSubstract(self.compensated, self.ponderated)
        result = ns((p,round(v,1)) for p,v in sorted(result.items()))
        return result

    def dump(self, data, description, filename):
        if description: step("Desant {} com a {}", description, filename)
        data.dump(filename)

    def reportCapacity(self):
        for person in self.limited:
            due = self.rounded.get(person,0)
            able = self.limited.get(person,0)
            if able == due:
                continue
            warn("Per indisponibilitats, {} no te capacitat per fer {} torns sino {}...",
                person, due, able)

    def dumpCsv(self, data, description, filename):
        if description: step("Desant {} com a {}", description, filename)
        content = '\n'.join(sorted(
            u'\t'.join([person]+[str(lineload) for lineload in lineloads])
            for person, lineloads in data.items()
        ))
        Path(filename).write_text(content, encoding='utf8')

    def summary(self):
        summaryColumns=ns()
        summaryColumns['Ideal'] = self.idealLoad
        summaryColumns['Proporcional'] = self.ponderated
        summaryColumns['Augmentada'] = self.augmented
        summaryColumns['CapacitatReal'] = self.loadCapacity
        summaryColumns['Topall'] = self.upperBound
        summaryColumns['AplicatTopall'] = self.limited
        summaryColumns['CobrintTorns'] = self.complete
        summaryColumns['CompensantDeutes'] = self.compensated
        summaryColumns['Final'] = self.final
        summaryColumns['Sobrecarrega'] = self.overload
        summaryColumns['CreditCarregat'] = self.loadedCredit
        summaryColumns['CreditInicial'] = self.initialCredit
        summaryColumns['CreditFinal'] = self.credits

        summary=ns()
        for column, data in summaryColumns.items():
            for person, value in data.items():
                summary.setdefault(person,ns())[column]=value

        summarycontent = '\n'.join([
            '\t'.join(['Nom'] + list(summaryColumns))
        ] + [
            '\t'.join([person] + [str(data.get(column,'-')) for column in summaryColumns])
            for person, data in summary.items()
        ])
        return summarycontent

    def outputResults(self, args):
        self.dump(self.ponderated, None, #"càrrega ponderada",
            "ponderatedideal-{}.yaml".format(self.monday))

        compensations = self.compensationsSummary()
        if compensations:
            success("    Compensacions fetes:\n{}",compensations)

        self.displayOverload()
        self.dump(self.overload, "sobrecàrrega",
            args.overload or "overload-{}.yaml".format(self.monday))

        for finalfile in [
            "carrega-{}.yaml".format(self.monday),
            args.weekshifts,
        ]:
            if not finalfile: continue
            self.dump(self.final, "càrrega final", finalfile)

        if hasattr(self, 'clusterized'):
            self.dumpCsv(self.clusterized, "càrrega distribuida en linies",
                "carrega-{}.csv".format(self.monday))
            # TODO: Unduplicate this
            self.dumpCsv(self.clusterized, "càrrega distribuida en linies",
                "carrega.csv".format(self.monday))

        finalLoad = self.finalLoad()
        if not self.final.get('ningu',0):
            success("S'ha aconseguit amb èxit una càrrega de {} torns", finalLoad)
        else:
            warn("No s'ha aconseguit una carrega de {}. S'han hagut d'omplir {} forats amb ningú", self.fullLoad, self.final.ningu)

        summary = self.summary()
        print(summary)
        if args.summary:
            Path(args.summary).write_text(summary, encoding='utf8')

def parseArgs():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--keep',
        action='store_true',
        help="no baixa les dades del drive"
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
        '--holidays',
        default='odoo',
        choices='drive notoi odoo'.split(),
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
        '--drive-file',
        help="Document del drive origen de dades externes"
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
        help="fitxer yaml de sortida amb la càrrega final de cada persona",
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

args=None

def main():
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

    global args

    args = parseArgs()

    step('Carregant configuració {}...', args.config_file)
    try:
        config = ns.load(args.config_file)
    except:
        error("Configuració incorrecta")
        raise

    config.personsfile = args.personsfile or config.get('personsfile', 'persons.yaml')
    if not args.keep and not args.personsfile:
        downloadPersons(config)

    from .persons import persons
    config.update(persons(config.get('personsfile',None)))

    if args.date is not None:
        # take the monday of the week including that date
        givenDate = datetime.datetime.strptime(args.date,"%Y-%m-%d").date()
        config.monday = addDays(givenDate, -givenDate.weekday())
    else:
        # If no date provided, take the next monday
        today = datetime.date.today()
        config.monday = addDays(today, 7-today.weekday())

    if args.lines:
        config.nTelefons = args.lines

    if args.drive_file:
        config.documentDrive = args.drive_file

    mustDownloadIdealShifts = not args.idealshifts and not config.get('idealshifts')
    config.idealshifts = config.get('idealshifts') or args.idealshifts or 'idealshifts.yaml'

    if not args.keep:
        step("Baixant persones de baixa del drive...")
        config.driveCertificate = args.certificate
        downloadLeaves(config, args.certificate)

        if mustDownloadIdealShifts:
            downloadIdealLoad(config, args.certificate)
        if not config.get('busyFiles'):
            downloadBusy(config)
            downloadFestivities(config)
            downloadVacations(config, source=args.holidays)

        step("Baixant bossa d'hores del tomatic...")
        downloadShiftCredit(config)

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
        forgive = args.forgive,
        inclusters = args.clusterize,
    )

    computer.outputResults(args)


if __name__ == '__main__':
    main()

# vim: et ts=4 sw=4
