#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from itertools import product as xproduct
from datetime import date, timedelta
import random
import datetime
import glob
import codecs
import requests
from builtins import range

from consolemsg import step, error, warn, out, u
from sheetfetcher import SheetFetcher
from .htmlgen import HtmlGen
from . import busy
import dbconfig
from pathlib2 import Path

# Dirty Hack: Behave like python3 open regarding unicode
def open(*args, **kwd):
    return codecs.open(encoding='utf8', *args, **kwd)

def transliterate(word):
    word=u(word).lower()
    for old, new in zip(
        u'àèìòùáéíóúçñ',
        u'aeiouaeioucn',
    ) :
        word = word.replace(old,new)
    return word

def createTable(defaultValue, *iterables) :
    """Creates a table with as many cells as the cross product of the iterables"""
    return dict((keys, defaultValue) for keys in xproduct(*iterables))

def baixaCarrega(config, certificat):
    step('Autentificant al Google Drive')
    fetcher = SheetFetcher(
        documentName=config.documentDrive,
        credentialFilename=certificat,
        )

    step('Baixant carrega setmanal...')

    carregaRangeName = config.intervalCarrega.format(
        *config.monday.timetuple())
    step("  Descarregant el rang '{}'...".format(carregaRangeName))
    carrega = fetcher.get_range(config.fullCarrega, carregaRangeName)
    step("  Guardant-ho com '{}'...".format(config.weekShifts))
    with open(config.weekShifts,'w') as phoneload :
        phoneload.write(
            "\n".join(
                '\t'.join(c for c in row)
                for row in carrega
                )
            )

def baixaPersones(config):
    step("Baixant informació de les persones del tomatic...")
    url = config.baseUrl + '/api/persons'
    r = requests.get(url)
    r.raise_for_status()
    from yamlns import namespace as ns
    persons = ns.loads(r.content)
    persons.persons.dump('persons.yaml')
    

def baixaIndisponibilitatsTomatic(config):
    step("Baixant indisponibilitats del tomatic...")

    baseUrl = config.baseUrl + '/api/busy/download/'
    for name, filename in [
            ('weekly', 'indisponibilitats.conf'),
            ('oneshot', 'oneshot.conf'),
        ]:
        url = baseUrl + name
        step("  Baixant {} from {}", filename, url)
        r = requests.get(url)
        r.raise_for_status()
        Path(filename).write_bytes(r.content)

def baixaVacancesDrive(config, certificat):

    fetcher = SheetFetcher(
        documentName=config.documentDrive,
        credentialFilename=certificat,
    )

    step('Baixant vacances del drive...')

    nextFriday = config.monday+timedelta(days=4)
    mondayYear = config.monday.year
    startingSemester = 1 if config.monday < date(mondayYear,7,1) else 2

    # HACK: Activate this flag until we have holidays spreadsheet for the new year
    if config.get("newYearHack",False):
        mondayYear-=1
        startingSemester = 2

    semesterFirsMonth = 1 if startingSemester is 1 else 7
    semesterFirstDay = date(mondayYear, semesterFirsMonth, 1)
    startingOffset = (config.monday - semesterFirstDay).days

    holidays2SRange = 'Vacances{}Semestre{}'.format(
        mondayYear,
        startingSemester,
        )
    step("  Baixant vacances de l'interval {}".format(holidays2SRange))
    holidays2S = fetcher.get_range(u(mondayYear), holidays2SRange)

    # TODO: Compose from two semesters (won't happen till 2018 Jan)
#    endingSemester = 1 if nextFriday < date(mondayYear,7,1) else 2
#    if startingSemester == endingSemester :
    who = [row[0] for row in holidays2S ]
    holidays = [
        (transliterate(name), [
            day for day, value in zip(
                ['dl','dm','dx','dj','dv'],
                row[startingOffset+1:startingOffset+6]
                )
            if value.strip()
            ])
        for name, row in zip(who, holidays2S)
        ]
    step("  Guardant indisponibilitats per vacances a 'indisponibilitats-vacances.conf'...")
    with open('indisponibilitats-vacances.conf','w') as holidaysfile:
        for name, days in holidays:
            for day in days:
                holidaysfile.write("+{} {} # vacances\n".format(name, day))


def baixaVacancesNotoi(config):
    step('Baixant vacances de no toi...')
    notoi = dbconfig.tomatic.notoi_data

    login = requests.post(
        notoi.service_url + notoi.login_ep,
        data={'username': notoi.user, 'password': notoi.password},
        verify=False
    )
    token = login.json()['token']
    firstDay = config.monday - timedelta(days=1)
    lastDay = config.monday + timedelta(days=5)
    next = notoi.service_url + notoi.query_ep.format(firstDay, lastDay)
    absences = []
    while(next):
        response = requests.get(
            next,
            headers={'Authorization': notoi.token_head + token},
            verify=False
        )
        next = response.json()['next']
        absences.extend(response.json()['results'])

    step("  Guardant indisponibilitats per vacances a 'indisponibilitats-vacances.conf'...")
    notoi_names = {}
    for key, value in config.notoi_ids.items():
        notoi_names[value] = key
    translate_days = ['dl', 'dm', 'dx', 'dj', 'dv']

    with open('indisponibilitats-vacances.conf', 'w') as holidaysfile:
        for absence in absences:
            name = notoi_names.get(absence['worker'])
            start = datetime.datetime.strptime(
                absence['start_time'],
                '%Y-%m-%dT%H:%M:%S'
            ).date()
            end = datetime.datetime.strptime(
                absence['end_time'],
                '%Y-%m-%dT%H:%M:%S'
            ).date()
            days = [
                translate_days[day]
                for day in range(5)
                if start <= config.monday + timedelta(days=day) <= end
            ]
            for day in days:
                out("+{} {} # vacances", name, day)
                holidaysfile.write("+{} {} # vacances\n".format(name, day))


class Backtracker(object):
    class ErrorConfiguracio(Exception): pass

    def __init__(self, config) :

        self.config = config
        self.outputFile = "graella-telefons-{}.html".format(config.monday)
        self.outputYaml = "graella-telefons-{}.yaml".format(config.monday)
        self.storedCost = ('uncomparableSize', 'uncomparablePenalty')
        self.globalMaxTurnsADay = config.maximHoresDiariesGeneral

        # Dimensional variables
        self.ntelefons = config.nTelefons                               # Phone slots
        self.hours = self.llegeixHores()                                # Turns (1st, 2nd, 3rd or 4th)
        self.dies = config.diesCerca                                    # Days at week (mon, tues, ...)

        errorDays = set(self.dies) - set(config.diesVisualitzacio)
        if errorDays:
            raise Backtracker.ErrorConfiguracio(
                "Aquests dies no son a la llista de visualitzacio: {}".format(errorDays))

        # Main Solution
        self.caselles = list(xproduct(self.dies, range(len(self.hours)), range(self.ntelefons)))    # all (day,turn,slot) combinations required to be filled

        # Constraints
		
        self.torns = self.readShifts(config.weekShifts, self.ntelefons)   # Persons and slots to be done
        self.companys = list(self.torns.keys())                         # Persons only

        self.topesDiaris = self.llegeixTopesDiaris(self.companys)       # Person with it's day limit
        busyFiles = config.get('busyFiles',
            ['oneshot.conf']+
            glob.glob('indisponibilitats*.conf'))

        self.disponible = self.initBusyTable(*busyFiles)                # (day,turn,person) is available?
        self.undesiredShifts = self.initUndesiredTable(*busyFiles)                # (day,turn,person) reason

        self.teTelefon = createTable(False,  self.dies, range(len(self.hours)), self.companys)  # (day,turn,person) has phone?
        self.tePrincipal = createTable(0,  self.companys, self.dies)    # (person,day) first turns?
        self.horesDiaries = createTable(0,  self.companys, self.dies)   # (person,day) turns?

        self.taules = config.taules                                     # (person) table
        self.telefonsALaTaula = createTable(0,                          # (day,turn,table) phones actives?
            self.dies, range(len(self.hours)), set(self.taules.values()))

        # Number of hours available each day
        self.disponibilitatDiaria = dict(                               # (person,day) max possible turns
            ((nom,dia), min(
                self.maxTornsDiaris(nom),
                sum(
                    0 if self.isBusy(nom,dia,hora) else 1
                    for hora in range(len(self.hours)))
                ))
            for nom, dia in xproduct(self.companys, self.dies))

        # Groups by person
        self.personGroups = dict([                                      # (person) list of goups
            (company, [
                group
                for group, companysDelGrup in self.config.groups.items()
                if company in companysDelGrup])
            for company in self.companys
            ])

        # Checking group definitions
        for group, persons in self.config.groups.items():
            for person in persons:
                if person not in self.companys:
                    warn("'{}' es al grup '{}', però no es al fitxer de càrrega",
                        person, group)
        for groupConfig in (
                'minIdleInGroup',
                'maxPhoningInGroup',
                ):
            for group in self.config[groupConfig]:
                if group not in self.config.groups:
                    warn("Configuration '{}' uses group '{}' not defined in 'groups'",
                        groupConfig, group)

        # Persons on phone in each group
        self.phoningOnGroup = createTable(0,                            # (group,day,turn) phones actives
            self.config.groups.keys(),
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
                self.config.groups.items(),
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

    def readShifts(self, tornsfile, ntelefons):
        result = dict()
        with open(tornsfile) as thefile:
            for numline, line in enumerate(thefile):
                if not line.strip(): continue
                row = [col.strip() for col in line.split('\t') ]
                name = row[0]
                if len(row)!=ntelefons+1 :
                    raise Backtracker.ErrorConfiguracio(
                        "{}:{}: S'experaven {} telefons per {} pero tenim {}".format(
                            tornsfile, numline, ntelefons, name, len(row)-1
                        ))
                result[name] = [int(c) for c in row[1:]]

        # checks
        for telefon in range(ntelefons):
            horesTelefon = sum(v[telefon] for nom, v in result.items())
            if horesTelefon == len(self.dies)*len(self.hours):
                continue
            raise Backtracker.ErrorConfiguracio(
                "Les hores de T{} sumen {} i no pas {}, revisa {}".format(
                    telefon+1, horesTelefon, len(self.dies)*len(self.hours), tornsfile))
        if self.config.discriminateLines:
            return result
        return {
            name: [sum(values)]+(ntelefons-1)*[0]
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

    def maxTornsDiaris(self, company):
        return self.topesDiaris.get(company, self.globalMaxTurnsADay)


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
        availability = dict(
            ((dia,hora,nom), True)
            for nom, dia, hora in xproduct(self.companys, self.dies, range(len(self.hours)))
            )
        for filename in filenames:

            def errorHandler(msg):
                raise Backtracker.ErrorConfiguracio(
                    "{}:{}".format(filename, msg))

            with open(filename) as thefile:
                allentries = busy.parseBusy(thefile, errorHandler)
                thisweekentries = busy.onWeek(self.config.monday, allentries)
                for entry in thisweekentries:
                    if entry.optional and self.config.ignoreOptionalAbsences:
                        continue
                    for hora, isBusy in enumerate(entry.turns):
                        if isBusy!='1': continue
                        weekdays = [entry.weekday] if entry.weekday else self.dies
                        for dia in weekdays:
                            availability[dia, hora, entry.person] = False
        return availability

    def isBusy(self, person, day, hour):
        return not self.disponible[day, hour, person]

    def setBusy(self, person, day, hour, busy=True):
        self.disponible[day, hour, person] = not busy

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

        if motiu is 'TotColocat':
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

                """
                if self.pendingShifts(company,0) > diesRestants * self.config.maximsT1PerDia:
                    self.cut("T1RestantsIncolocables", partial,
                        "A {} li queden massa T1 per posar"
                        .format(company))
                    if isInfraSolution: return
                    cut=True # Report all the bad guys and cut later
                """
                tornsPendents = self.pendingShifts(company)
                tornsColocables = sum(
                    self.disponibilitatDiaria[company,dia]
                    for dia in self.dies[idia:]
                    )
                if tornsPendents > tornsColocables:
                    self.cut("RestantsIncolocables", partial,
                        "A {} nomes li queden {} forats per posar {} hores"
                        .format(company, tornsColocables, tornsPendents))
                    if isInfraSolution: return
                    cut=True # Report all the bad guys and cut later

            if cut: return

        if self.config.pruneRedundant:
            lastPersonInTurn = next((person for person in partial[:-1-telefon:-1] if person is not 'ningu'), None)
            companys = [person for person in self.companys if not lastPersonInTurn or person > lastPersonInTurn]
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
            taula=self.taules[company]

            # Reasons to prune chosing that person

            # Force ordered persons within a turn to avoid redundant paths
            # Prefilter should do but forced may introduce them again
            if self.config.pruneRedundant:
                if lastPersonInTurn and company is not 'ningu' and lastPersonInTurn > company:
                    self.cut("Redundant", partial,
                        "Cami redundant, noms no ordenats {} -> {}"
                        .format(partial[-1], company))
                    continue

            # Person has no turns left to do
            if self.pendingShifts(company, telefon) <= 0:
                self.cut("TotColocat", partial,
                    "{} ja ha exhaurit els seus torns de linia {}aria"
                    .format( company, telefon+1))
                continue

            # Person busy in this turn (it has another line in this turn or it is unavailable)
            if self.isBusy(company, day, hora):
                self.cut("Indisponible", partial,
                    "{} no esta disponible el {} a {}a hora"
                    .format( company, day, hora+1))
                continue

            # Its a main line and person already has taken a main line that day
            """
            if telefon==0 and self.tePrincipal[company, day] >= self.config.maximsT1PerDia:
                self.cut("MassesPrincipals", partial,
                    "Dos principals per {} el {} no, sisplau"
                    .format(company,day))
                continue
            """

            # Reduce cacophonies, by limiting people in the same table at once
            if taula!=-1 and self.telefonsALaTaula[day, hora, taula]>=self.config.maximPerTaula :
                self.cut("TaulaSorollosa", partial,
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
            if self.horesDiaries[company, day] >= self.maxTornsDiaris(company):
                self.cut("DiaATope", partial,
                    "No li posem mes a {} que ja te {} hores el {}"
                    .format( company, self.horesDiaries[company, day], day))
                continue

            # Allow lunch break, do no take both central hours one day
            if self.config.deixaEsmorzar and company not in self.config.noVolenEsmorzar:
                if hora==2 and self.teTelefon[day, 1, company]:
                    self.cut("Esmorzar", partial,
                        "{} es queda sense esmorzar el {}"
                        .format(company, day))
                    continue

            # Reasons to penalize chosing that person

            def penalize(value, short, reason):
                penalties.append((value,reason))
                return value

            if hora and self.horesDiaries[company, day] and not self.teTelefon[day, hora-1, company]:
                if self.maxTornsDiaris(company) < 3:
                    self.cut("Discontinu", partial,
                        "{} te hores separades el {}".format(company,day))
                    continue

                if self.config.costHoresDiscontinues:
                    cost += penalize(self.config.costHoresDiscontinues, "Discontinu",
                        "{} te hores separades el {}".format(company, day))

            undesiredReason = self.isUndesiredShift(company, day, hora)
            if undesiredReason:
                cost += penalize(self.config.costHoraNoDesitjada, "Undesired",
                    u"{} fa {} a {}a hora que no li va be perque: \"{}\""
                    .format(company, day, hora+1, undesiredReason))

            if self.horesDiaries[company, day]>0 :
                cost += penalize(
                    self.config.costHoresConcentrades * self.horesDiaries[company, day],
                    "Repartiment",
                    "{} te mes de {} hores el {}".format(company, self.horesDiaries[company, day], day))

            if taula!=-1 and self.telefonsALaTaula[day, hora, taula]>0 :
                cost += penalize(
                    self.config.costTaulaSorollosa * self.telefonsALaTaula[day, hora, taula],
                    "Ocupacio",
                    "{} te {} persones a la mateixa taula amb telefon a {}a hora del {}".format(
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
        if firstAtCost:
            # Is the first that good, start from scratch
            self.storedCost = (len(partial), cost)
            personalColors = htmlgen.htmlColors()
            header = htmlgen.htmlHeader()
            subheader = htmlgen.htmlSubHeader()
            htmlgen.getYaml().dump(self.outputYaml)
            with open(self.outputFile,'w') as output:
                output.write(
                    header+
                    personalColors+
                    subheader+
                    htmlgen.htmlSetmana()
                )
            with open(self.config.monitoringFile,'w') as output:
                output.write(
                    header+
                    personalColors+
                    subheader
                )

        penalitzacions = (
            htmlgen.htmlPenalizations(
                cost,
                penalties
            )
        )
        with open(self.config.monitoringFile,'a') as output:
            output.write(htmlgen.htmlTable())
            output.write(penalitzacions)
        if firstAtCost:
            yaml = htmlgen.getYaml()
            yaml.penalties = penalties
            yaml.cost = cost
            yaml.dump(self.outputYaml)

            with open(self.outputFile,'a') as output:
                output.write(
                    htmlgen.htmlTable()+
                    htmlgen.htmlExtensions()+
                    htmlgen.htmlFixExtensions()+
                    htmlgen.htmlFooter()
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
        '--holidays',
        default='drive',
        help="Origen d'on agafa les vacances",
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
        '--config-file',
        default='config.yaml',
        help="fitxer de configuració pincipal",
    )

    parser.add_argument(
        '--weekshifts',
        default=None,
        help="fitxer tsv amb la carrega a cada torn (columna) de cada persona (fila)",
    )

    return parser.parse_args()

args=None

def main():
    global args

    args = parseArgs()

    step('Carregant configuració {}...', args.config_file)
    from yamlns import namespace as ns
    try:
        config = ns.load(args.config_file)
    except:
        error("Configuració incorrecta")
        raise

    if not args.keep:
        baixaPersones(config)

    personsPath = Path('persons.yaml')
    if personsPath.exists():
        config.update(ns.load(str(personsPath)))

    if args.date is not None:
        # take the monday of the week including that date
        givenDate = datetime.datetime.strptime(args.date,"%Y-%m-%d").date()
        config.monday = givenDate - timedelta(days=givenDate.weekday())
    else:
        # If no date provided, take the next monday
        today = date.today()
        config.monday = today + timedelta(days=7-today.weekday())

    if args.drive_file:
        config.documentDrive = args.drive_file

    mustDownloadShifts = not args.weekshifts and not config.get('weekShifts')
    config.weekShifts = config.get('weekShifts') or args.weekshifts or 'carrega.csv'

    if not args.keep:
        if mustDownloadShifts:
            baixaCarrega(config, args.certificate)
        if not config.get('busyFiles'):
            baixaIndisponibilitatsTomatic(config)
            if args.holidays == 'notoi':
                baixaVacancesNotoi(config)
            else: # args.holidays == 'drive':
                baixaVacancesDrive(config, args.certificate)

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
