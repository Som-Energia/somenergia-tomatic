#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import product as xproduct
import random
from pathlib import Path
import datetime

from consolemsg import step, error, warn, out, u
from yamlns import namespace as ns

from .htmlgen import HtmlGen
from . import busy
from .shiftload import ShiftLoadComputer
from .persons import persons


# Dirty Hack: Behave like python3 open regarding unicode
def open(filename, *args, **kwd):
    return Path(filename).open(encoding='utf8', *args, **kwd)

def createTable(defaultValue, *iterables) :
    """Creates a table with as many cells as the cross product of the iterables"""
    return dict((keys, defaultValue) for keys in xproduct(*iterables))


class Backtracker(object):
    class ErrorConfiguracio(Exception): pass

    def __init__(self, config) :

        self.config = config
        self.outputFile = "graella-telefons-{}.html".format(config.monday)
        self.outputYaml = "graella-telefons-{}.yaml".format(config.monday)
        self.storedCost = ('uncomparableSize', 'uncomparablePenalty')
        self.globalMaxTurnsADay = config.maximHoresDiariesGeneral

        # Dimensional variables
        self.nlines = config.nTelefons
        self.hours = self.llegeixHores()
        self.dies = config.diesCerca

        errorDays = set(self.dies) - set(config.diesVisualitzacio)
        if errorDays:
            raise Backtracker.ErrorConfiguracio(
                "Aquests dies no son a la llista de visualitzacio: {}".format(errorDays))

        workDays = busy.laborableWeekDays(config.monday)
        if set(workDays) - set(self.dies):
            warn("T'has deixat dies laborables: {}"
                .format(sorted([x for x in set(workDays)-set(self.dies)])))

        if set(self.dies) - set(workDays):
            warn(u"No s'inclouran els dies festius: {}."
                .format(', '.join((x for x in self.dies if x not in workDays))))

        self.dies = [day for day in self.dies if day in workDays]

        self.overload = ns.load(config.overloadfile)

        # Main Solution
        self.caselles = list(xproduct(self.dies, range(len(self.hours)), range(self.nlines)))    # all (day,turn,slot) combinations required to be filled

        # Constraints

        self.torns = self.readShifts(config.weekShifts, self.nlines)   # Persons and slots to be done
        self.companys = list(self.torns.keys())                         # Persons only
        if not config.aleatori:
            self.companys.sort()

        self.dailyLimitByPerson = self.llegeixTopesDiaris(self.companys)       # Person with it's day limit
        busyFiles = config.get('busyFiles', [
            'oneshot.conf',
            'indisponibilitats.conf',
            'indisponibilitats-vacances.conf',
            ])

        self.busy = self.initBusyTable(*busyFiles)                # (day,turn,person) is available?
        self.busyReasons = self.busy.explain()
        self.undesiredShifts = self.initUndesiredTable(*busyFiles)                # (day,turn,person) reason

        self.teTelefon = createTable(False,  self.dies, range(len(self.hours)), self.companys)  # (day, hour,person) has phone?
        self.tePrincipal = createTable(0,  self.companys, self.dies)    # (person,day) first turns?
        self.horesDiaries = createTable(0,  self.companys, self.dies)   # (person,day) turns?
        self.ningusPerTurn = createTable(0, self.dies, range(len(self.hours))) # (day, hour)

        self.tables = config.get('tables',{})                           # (person) table
        self.telefonsALaTaula = createTable(0,                          # (day,turn,table) phones actives?
            self.dies, range(len(self.hours)), set(self.tables.values() or [-1]))

        # Number of hours available each day
        self.disponibilitatDiaria = dict(                               # (person,day) max possible turns
            ((nom,dia), min(
                self.personDailyLimit(nom),
                sum(
                    0 if self.isBusy(nom,dia,hora) else 1
                    for hora in range(len(self.hours)))
                ))
            for nom, dia in xproduct(self.companys, self.dies))

        # Groups by person
        groups = self.config.get('groups',{})
        self.personGroups = dict([                                      # (person) list of goups
            (company, [
                group
                for group, companysDelGrup in groups.items()
                if company in companysDelGrup])
            for company in self.companys
            ])

        # Checking group definitions
        for group, persons in groups.items():
            for person in persons:
                if person not in self.companys:
                    warn("'{}' es al grup '{}', però no es al fitxer de càrrega",
                        person, group)
        for groupConfig in (
                'minIdleInGroup',
                'maxPhoningInGroup',
                ):
            for group in self.config[groupConfig]:
                if group not in groups:
                    warn("Configuration '{}' uses group '{}' not defined in 'groups'",
                        groupConfig, group)

        # Persons on phone in each group
        self.phoningOnGroup = createTable(0,                            # (group,day,turn) phones actives
            groups.keys(),
            self.dies,
            range(len(self.hours)),
            )

        # Idle persons in each group (not busy nor on phone)
        self.idleInGroup = dict([                                       # (group,day,turn) available persons in group
            (
                (group, dia, hora),
                sum(
                    0 if self.isBusy(person,dia,hora) else 1
                    for person in persons
                    if person in self.companys
                ))
            for (group, persons), dia, hora
            in xproduct(
                groups.items(),
                self.dies,
                range(len(self.hours)),
                )
            ])

        # Visited nodes
        self.nbactracks = 0
        # Max number of visited
        self.backtrackDepth = config.backtrackDepth
        # Number of visited nodes befor trying another path in random mode
        self.maxNodesToPersevere = config.maxNodesToPersevere

        self.cutLog = {}
        self.deeperCutDepth = 0
        self.deeperCutLog = set()

        # just for tracking
        self.bestSolution = []
        self.bestCost = 1000000000

        self.cost = 0
        self.cutoffCost = config.costLimit
        self.penalties=[]

        self.terminated=False

    def llegeixHores(self):
        lines = [u(h) for h in self.config.hours ]
        return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]

    def readShifts(self, tornsfile, nlines):
        result = dict()
        with open(tornsfile) as thefile:
            for numline, line in enumerate(thefile):
                if not line.strip(): continue
                row = [col.strip() for col in line.split('\t') ]
                name = row[0]
                if len(row)!=nlines+1 :
                    raise Backtracker.ErrorConfiguracio(
                        "{}:{}: S'experaven {} telefons per {} pero tenim {}".format(
                            tornsfile, numline, nlines, name, len(row)-1
                        ))
                result[name] = [int(c) for c in row[1:]]

        # checks
        for telefon in range(nlines):
            horesTelefon = sum(v[telefon] for nom, v in result.items())
            if horesTelefon == len(self.dies)*len(self.hours):
                continue
            raise Backtracker.ErrorConfiguracio(
                "Les hores de L{} sumen {} i no pas {}, revisa {}".format(
                    telefon+1, horesTelefon, len(self.dies)*len(self.hours), tornsfile))
        if self.config.discriminateLines:
            return result
        return {
            name: [sum(values)]+(nlines-1)*[0]
            for name, values in result.items()
            }

    def pendingShifts(self, person, line=None):
        if not self.config.discriminateLines: line = 0
        if line is not None:
            return self.torns[person][line]
        return sum(self.torns[person])

    def useShift(self, person, line):
        if not self.config.discriminateLines: line = 0
        self.torns[person][line]-=1

    def unuseShift(self, person, line):
        if not self.config.discriminateLines: line = 0
        self.torns[person][line]+=1


    def llegeixTopesDiaris(self, persons) :
        dailyMaxPerPerson = dict(
            (nom, int(value))
            for nom, value
            in self.config.maximHoresDiaries.items()
            )
        for name in dailyMaxPerPerson:
            if name in persons: continue
            raise Backtracker.ErrorConfiguracio(
                "El nom '{}' de maximHoresDiaries a config.yaml no surt a carrega.csv"
                .format(name))
        return dailyMaxPerPerson

    def personDailyLimit(self, company):
        return self.dailyLimitByPerson.get(company, self.globalMaxTurnsADay)


    def initUndesiredTable(self, *filenames) :
        #if self.config.ignoreOptionalAbsences: return dict()

        undesired = dict()
        for filename in filenames:
            def errorHandler(msg):
                raise Backtracker.ErrorConfiguracio(
                    "{}:{}".format(filename, msg))

            with open(filename) as thefile:
                allentries = busy.parseBusy(thefile, errorHandler)
                thisweekentries = busy.onWeek(self.config.monday, allentries)
                for entry in thisweekentries:
                    if not entry.optional:
                        continue
                    for hora, isBusy in enumerate(entry.turns):
                        if isBusy!='1': continue
                        weekdays = [entry.weekday] if entry.weekday else self.dies
                        for dia in weekdays:
                            undesired[dia, hora, entry.person] = entry.reason
        return undesired

    def isUndesiredShift(self, person, day, hour):
        return self.undesiredShifts.get((day, hour, person), False)

    def initBusyTable(self, *filenames) :
        table = busy.BusyTable(
            persons = self.companys,
            days = self.dies,
            nhours = len(self.hours),
        )
        for filename in filenames:
            def errorHandler(msg):
                raise Backtracker.ErrorConfiguracio(
                    "{}:{}".format(filename, msg))

            table.load(
                filename,
                monday = self.config.monday,
                errorHandler = errorHandler,
                justRequired = self.config.ignoreOptionalAbsences,
            )
        return table

    def isBusy(self, person, day, hour):
        return self.busy.isBusy(day, hour, person)

    def setBusy(self, person, day, hour, busy=True):
        if person == 'ningu': return
        self.busy.setBusy(day, hour, person, busy)

    def printCuts(self):
        out("Raons de tall a cada nivell")
        for (depth, motiu), many in sorted(self.cutLog.items()):
            out("{} {} {}", depth, motiu, many)

    def cut(self, motiu, partial, log=None):
        try:
            self.cutLog[len(partial), motiu]+=1
        except KeyError:
            self.cutLog[len(partial), motiu]=1

        message = log or motiu

        if motiu in args.verbose or 'all' in args.verbose:
            warn(message)

        # Do not log when a more complete solution solution exists
        if self.deeperCutLog and self.deeperCutDepth > len(partial): return

        if self.deeperCutDepth < len(partial):
            self.deeperCutLog = set()
            self.deeperCutDepth = len(partial)

        if motiu == 'FullLoad':
            return # Not worth to log

        with open(self.config.monitoringFile,'a') as output:
            output.write("<div class='error'>Incompletable: ")
            output.write(u(message))
            output.write("</div>")

        if message in self.deeperCutLog:
            return

        warn(message)
        self.deeperCutLog.add(message)


    def solve(self) :
        self.nbactracks = 0
        while not self.terminated:
            self.perseveredNodes = 0
            self.solveTorn([])
            if self.backtrackDepth and self.nbactracks > self.backtrackDepth:
                break # Too long

            if self.config.aleatori and self.perseveredNodes > self.maxNodesToPersevere:
                step("Massa estona en aquest camí sense solucions que superin {}/{} amb cost {}",
                    len(self.bestSolution), len(self.caselles), self.bestCost)
                continue

            break # Full backtrack completed

        if len(self.bestSolution) != len(self.caselles):
            self.printCuts()
            error("Impossible trobar solució\n{}"
                .format( '\n'.join(sorted(self.deeperCutLog))))
        else:
            step("Millor graella grabada a '{}'".format(self.outputFile))
            step("Millor graella grabada a '{}'".format(self.outputYaml))

    def solveTorn(self, partial):
        if self.cutoffCost <= self.config.get("stopPenalty",0):
            self.terminated = True

        if self.terminated: return

        # A more complete solution is always better
        # Better solution found? Report and hold it
        if (len(self.bestSolution), -self.bestCost) <= (len(partial), -self.cost):
            if len(self.bestSolution) < len(partial) or len(partial)==len(self.caselles):
                self.perseveredNodes=0 # chill, we found something!

            if len(partial) == len(self.caselles):
                out("Solució trobada amb cost {}.", self.cost)
            else:
                out("Solució incomplerta {}/{} caselles, cost {}",
                    len(partial), len(self.caselles), self.cost)
            self.reportSolution(partial, self.cost, self.penalties)
            self.bestSolution=list(partial)
            self.bestCost=self.cost

        # Complete solution? Stop backtracking.
        if len(partial) == len(self.caselles):
            self.cutoffCost = self.cost
            self.reportSolution(partial, self.cost, self.penalties)
            return

        day, hora, telefon = self.caselles[len(partial)] # (day,turn,slot) to be filled

        # Comencem dia, mirem si podem acomplir els objectius amb els dies restants
        if telefon==0 and hora==0:

            idia = self.dies.index(day)
            diesRestants =  len(self.dies)-idia

            # TODO: Heuristica que pot tallar bones solucions
            if self.config.descartaNoPrometedores :
                if idia and self.cost*len(self.dies) / idia > self.cutoffCost:
                    self.cut("NoEarlyCost", partial,
                        "Tallant una solucio poc prometedora")
                    return

            cut=False
            isInfraSolution = len(partial)<len(self.bestSolution)
            for company in self.companys:

                if self.config.discriminateLines:
                    if self.pendingShifts(company,0) > diesRestants * self.config.maximsT1PerDia:
                        self.cut("L1RestantsIncolocables", partial,
                            "A {} li queden massa L1 per posar"
                            .format(company))
                        if isInfraSolution: return
                        cut=True # Report all the bad guys and cut later

                tornsPendents = self.pendingShifts(company)
                tornsColocables = sum(
                    self.disponibilitatDiaria[company,dia]
                    for dia in self.dies[idia:]
                    )
                if company != 'ningu' and tornsPendents > tornsColocables:
                    self.cut("UnableToAllocateLoad", partial,
                        "A {} nomes li queden {} forats per posar {} hores"
                        .format(company, tornsColocables, tornsPendents))
                    if isInfraSolution: return
                    cut=True # Report all the bad guys and cut later

            if cut: return

        if self.config.pruneRedundant:
            # Last non-nigu person within the turn if any
            lastPersonInTurn = next((person for person in partial[:-1-telefon:-1] if person != 'ningu'), None)
            # Just take persons alfabetically greater than the last one if any
            companys = [
                person
                for person in self.companys
                if not lastPersonInTurn
                or person > lastPersonInTurn
            ]
        else:
            companys=self.companys[:]

        if self.config.aleatori:
            random.shuffle(companys)

        # Is forced position? Take it
        if (day, hora+1, telefon+1) in self.config.forced:
            companys = [self.config.forced[(day,hora+1,telefon+1)]]

        for company in companys:

            cost = 0
            penalties = []
            taula=self.tables.get(company,-1)

            # Reasons to prune chosing that person

            # Force ordered persons within a turn to avoid redundant paths
            # Prefilter should do but forced may introduce them again
            if self.config.pruneRedundant:
                if lastPersonInTurn and company != 'ningu' and lastPersonInTurn > company:
                    self.cut("Redundant", partial,
                        "Cami redundant, noms no ordenats {} -> {}"
                        .format(partial[-1], company))
                    continue

            # Person has no turns left to do
            if self.pendingShifts(company, telefon) <= 0:
                self.cut("FullLoad", partial,
                    "{} ja ha exhaurit els seus torns de linia {}aria"
                    .format( company, telefon+1))
                continue

            # Person busy in this turn (it has another line in this turn or it is unavailable)
            if self.isBusy(company, day, hora) and company != 'ningu' :
                self.cut("Busy", partial,
                    "{} no esta disponible el {} a {}a hora"
                    .format( company, day, hora+1))
                continue

            # Its a main line and person already has taken a main line that day
            if self.config.discriminateLines:
                if telefon==0 and self.tePrincipal[company, day] >= self.config.maximsT1PerDia:
                    self.cut("MassesPrincipals", partial,
                        "Dos principals per {} el {} no, sisplau"
                        .format(company,day))
                    continue

            # Reduce cacophonies, by limiting people in the same table at once
            if taula!=-1 and self.telefonsALaTaula[day, hora, taula]>=self.config.maximPerTaula :
                self.cut("Crosstalk", partial,
                    "{} ja té {} persones a la mateixa taula amb telefon a {}a hora del {}"
                    .format(company, self.telefonsALaTaula[day, hora, taula], hora+1, day))
                continue

            # Ensure groups with a minimum of idle persons
            def notEnoughIdleInGroup(company):
                for group in self.personGroups[company] :
                    if group not in self.config.minIdleInGroup: continue
                    minIdle = self.config.minIdleInGroup[group]
                    if self.idleInGroup[group, day, hora] > minIdle+1:
                        continue
                    return ("El grup {} on pertany {} no tindria {} persones alliberades el {} a {} hora"
                        .format(group, company, minIdle, day, hora+1))
                return False

            if notEnoughIdleInGroup(company):
                self.cut("NotEnoughIdleInGroup", partial, notEnoughIdleInGroup(company))
                continue

            # Ensure groups with a maximum phoning persons
            def tooManyPhoningOnGroup(company):
                for group in self.personGroups[company] :
                    if group not in self.config.maxPhoningInGroup: continue
                    maxPhoning = self.config.maxPhoningInGroup[group]
                    if self.phoningOnGroup[group, day, hora] < maxPhoning:
                        continue
                    return ("El grup {} on pertany {} ja te {} persones al telèfon el {} a {} hora"
                        .format(group, company, maxPhoning, day, hora+1))
                return False

            if tooManyPhoningOnGroup(company):
                self.cut("TooManyLinesForGroup", partial, tooManyPhoningOnGroup(company))
                continue

            # Limit the number of daily turns
            if company != 'ningu' and self.horesDiaries[company, day] >= self.personDailyLimit(company):
                self.cut("FullDay", partial,
                    "No li posem mes a {} que ja te {} hores el {}"
                    .format( company, self.horesDiaries[company, day], day))
                continue

            # Allow lunch break, do no take both central hours one day
            if self.config.deixaEsmorzar and company not in self.config.noVolenEsmorzar:
                if hora==2 and self.teTelefon[day, 1, company]:
                    self.cut("Brunch", partial,
                        "{} es queda sense esmorzar el {}"
                        .format(company, day))
                    continue

            if company == "ningu" and self.ningusPerTurn[day,hora] == self.config.maxNingusPerTurn:
                self.cut(
                    "TooManyConcurrentHoles",
                    partial,
                    "Hi ha masses forats a {}a hora del {}".format(hora+1, day)
                )
                continue

            # Reasons to penalize chosing that person

            def penalize(value, short, reason):
                penalties.append((value,reason))
                return value

            if hora and self.horesDiaries[company, day] and not self.teTelefon[day, hora-1, company]:
                if self.personDailyLimit(company) < 3:
                    self.cut("Discontinuous", partial,
                        "{} te hores separades el {}".format(company,day))
                    continue

                if self.config.costHoresDiscontinues:
                    cost += penalize(self.config.costHoresDiscontinues, "Discontinuous",
                        "{} te hores separades el {}".format(company, day))

            if company == "ningu":
                cost += penalize(self.config.costTornBuit * (self.ningusPerTurn[day,hora]+1),
                    "ConcurrentHoles",
                    u"Hi ha {} torns buits a {}a hora del {}".format(
                        self.ningusPerTurn[day,hora]+1,
                        hora+1,
                        day,
                    )
                )

            undesiredReason = self.isUndesiredShift(company, day, hora)
            if undesiredReason:
                cost += penalize(self.config.costHoraNoDesitjada, "Undesired",
                    u"{} fa {} a {}a hora que no li va be perque: \"{}\""
                    .format(company, day, hora+1, undesiredReason))

            if self.horesDiaries[company, day]>0 :
                cost += penalize(
                    self.config.costHoresConcentrades * self.horesDiaries[company, day],
                    "ConcentratedLoad",
                    u"{} té més de {} hores el {}".format(company, self.horesDiaries[company, day], day))

            if taula!=-1 and self.telefonsALaTaula[day, hora, taula]>0 :
                cost += penalize(
                    self.config.costTaulaSorollosa * self.telefonsALaTaula[day, hora, taula],
                    "Crosstalk",
                    u"{} té altres {} persones amb telèfon a la mateixa taula a {}a hora del {}".format(
                        company, self.telefonsALaTaula[day, hora, taula], hora+1, day))

            # If penalty is too high also prune

            if self.cost + cost > self.cutoffCost :
                self.cut("TooMuchCost", partial,
                    "Afegir {} suma masa cost: {}"
                    .format(company, self.cost+cost))
                break

            # (Over?)Pruning solutions which have the same cost than

            if self.cost + cost == self.cutoffCost and len(partial)<len(self.caselles)*0.7 :
                self.cut("CostEqual", partial,
                    "Solucio segurament massa costosa, no perdem temps: {}"
                    .format(self.cost+cost))
                break

            if self.config.mostraCami or args.track:
                if len(partial) < self.config.maximCamiAMostrar :
                    out("  "*len(partial)+company[:2])

            def markGroups(company, day, hora):
                for g in self.personGroups[company] :
                    self.idleInGroup[g, day, hora] -= 1
                    self.phoningOnGroup[g, day, hora] +=1

            def unmarkGroups(company, day, hora):
                for g in self.personGroups[company] :
                    self.idleInGroup[g, day, hora] += 1
                    self.phoningOnGroup[g, day, hora] -=1

            # Anotem la casella
            if company == "ningu":
                self.ningusPerTurn[day,hora] += 1
            self.cost += cost
            self.penalties += penalties
            #if telefon == 0: self.tePrincipal[company, day]+=1
            self.teTelefon[day, hora, company]=True
            self.setBusy(company,day,hora)
            self.horesDiaries[company,day]+=1
            self.useShift(company, telefon)
            self.telefonsALaTaula[day,hora,taula]+=1
            markGroups(company,day,hora)

            # Provem amb la seguent casella
            self.solveTorn(partial+[company])
            self.nbactracks += 1
            self.perseveredNodes += 1

            # Desanotem la casella
            if company == "ningu":
                self.ningusPerTurn[day,hora] -= 1
            unmarkGroups(company,day,hora)
            self.telefonsALaTaula[day,hora,taula]-=1
            self.unuseShift(company, telefon)
            self.horesDiaries[company,day]-=1
            self.setBusy(company,day,hora, False)
            self.teTelefon[day, hora, company]=False
            #if telefon == 0: self.tePrincipal[company, day]-=1
            if penalties:
                del self.penalties[-len(penalties):]
            self.cost -= cost

            # Si portem massa estona explorant el camí parem i provem un altre
            if self.config.aleatori and self.perseveredNodes > self.maxNodesToPersevere:
                break
            if self.nbactracks > self.backtrackDepth:
                break

    def reportSolution(self, partial, cost, penalties=[]) :
        firstAtCost = self.storedCost != (len(partial), cost)
        paddedPartial = partial + ['?']*(len(self.caselles)-len(partial))
        solution = dict(zip(self.caselles, paddedPartial))
        htmlgen=HtmlGen.fromSolution(self.config,solution,self.config.monday)
        timetable = htmlgen.getYaml()
        # TODO: This should be passed to fromSolution with defaults
        timetable.overload = self.overload
        timetable.penalties = penalties
        timetable.cost = cost
        if firstAtCost:
            # Is the first that good, start from scratch
            self.storedCost = (len(partial), cost)
            timetable.dump(self.outputYaml)
            personalColors = htmlgen.htmlColors()
            header = htmlgen.htmlHeader()
            subheader = htmlgen.htmlSubHeader()
            with open(self.outputFile,'w') as output:
                output.write(
                    header+
                    personalColors+
                    subheader+
                    htmlgen.htmlSetmana() +
                    htmlgen.htmlTable()+
                    htmlgen.htmlPenalties()+
                    htmlgen.htmlExtensions()+
                    htmlgen.htmlFooter()
                )
            with open(self.config.monitoringFile,'w') as output:
                output.write(
                    header+
                    personalColors+
                    subheader
                )

        penalitzacions = (
            htmlgen.htmlPenalties()
        )
        with open(self.config.monitoringFile,'a') as output:
            output.write(htmlgen.htmlTable())
            output.write(penalitzacions)

        # Dump status for the planer executor
        if firstAtCost:
            unfilled="Complete"
            busyReasons={}
            if len(partial)<len(self.caselles):
                day, itime, line = self.caselles[len(partial)]
                time = self.config.hours[itime]
                unfilled = "{} {} L{}".format(day, time, line+1)
                busyReasons = self.busyReasons.get((day, itime), [])
            ns(
                totalCells=len(self.caselles),
                completedCells=len(partial),
                solutionCost=cost,
                timeOfLastSolution=u(datetime.datetime.utcnow()),
                unfilledCell=unfilled,
                busyReasons=busyReasons,
                penalties=penalties,
            ).dump('status-temp.yaml')
            # To avoid reading half written files
            Path('status-temp.yaml').rename('status.yaml')

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

args=None

def main():
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

    global args

    args = parseArgs()

    step('Carregant configuració {}...', args.config_file)
    try:
        config = ns.load(args.config_file)
    except:
        error("Configuració incorrecta")
        raise

    if args.personsfile:
        config.personsfile = args.personsfile

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

    config.computeShifts = config.get('computeShifts') or args.compute_shifts

    mustDownloadIdealShifts = not args.idealshifts and not config.get('idealshifts')
    config.idealshifts = config.get('idealshifts') or args.idealshifts or 'idealshifts.yaml'

    mustDownloadShifts = not args.weekshifts and not config.get('weekShifts') and not config.computeShifts
    config.weekShifts = config.get('weekShifts') or args.weekshifts or 'carrega.csv'

    mustDownloadOverload = not args.overload and not config.computeShifts
    config.overloadfile = args.overload or "overload-{}.yaml".format(config.monday)

    if not args.keep:
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
            step("Baixant bossa d'hores del tomatic...")
            downloadShiftCredit(config)

    if config.computeShifts:
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
            inclusters = args.clusterize or config.get('clusterize', False),
        )

        computer.outputResults(args)

    if args.search_days:
        config.diesCerca = args.search_days.split(',')

    if args.stop_penalty:
        config.stopPenalty = args.stop_penalty

    if args.deterministic:
        config.aleatori = not args.deterministic


    import signal

    def signal_handler(signal, frame):
        warn('You pressed Ctrl-C!')
        b.terminated = True

    signal.signal(signal.SIGINT, signal_handler)

    step('Muntant el solucionador...')
    try:
        b = Backtracker(config)
    except:
        error("Configuració incorrecta")
        raise

    step('Generant horari...')
    b.solve()


if __name__ == '__main__':
    main()

# vim: et ts=4 sw=4
