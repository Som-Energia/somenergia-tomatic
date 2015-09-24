#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import product as xproduct
import random
from datetime import date, timedelta
import datetime
import glob
from consolemsg import step, error, warn, fail
import codecs
import sys


def iniciSetmana():
    dateProvided = len(sys.argv)>1
    
    if dateProvided:
         # take the monday of the week including that date
        date = datetime.datetime.strptime(sys.argv[1],"%Y-%m-%d").date()
        return date - timedelta(days=date.weekday())

    # If no date provided, take the next monday
    today = date.today()
    return today + timedelta(days=7-today.weekday())

def baixaDades(monday) :
    def table(sheet, name):
        cells = sheet.range(name)
        width = cells[-1].col-cells[0].col +1
        height = cells[-1].row-cells[0].row +1
        return [ 
            [cell.value for cell in row]
            for row in zip( *(iter(cells),)*width)
            ]

    import json
    import gspread
    from oauth2client.client import SignedJwtAssertionCredentials

    step('Autentificant al Google Drive')
    credential = 'drive-certificate.json'
    name = 'Quadre de Vacances'

    json_key = json.load(open(credential))

    credentials = SignedJwtAssertionCredentials(
        json_key['client_email'],
        json_key['private_key'],
        scope = ['https://spreadsheets.google.com/feeds']
        )

    gc = gspread.authorize(credentials)
    try:
        doc = gc.open(name)
    except:
        error("No s'ha trobat el document, potser no li has donat permisos a l'aplicacio")
        error("Cal compartir el document '{}' amb el següent correu:".format(name))
        error(json_key['client_email'])
        sys.exit(-1)

    carregaRangeName = 'Carrega_{:02d}_{:02d}_{:02d}'.format(
        *monday.timetuple())
    step('Baixant carrega setmanal del rang {}...'.format(carregaRangeName))

    carregaSheet = doc.get_worksheet(6)
    carrega = table(carregaSheet, carregaRangeName)
    with open('carrega.csv','w') as phoneload :
        phoneload.write(
            "\n".join(
                '\t'.join(c for c in row)
                for row in carrega
                )
            )

    step('Baixant vacances...')

    def transliterate(word):
        word=unicode(word).lower()
        for old, new in zip(
            u'àèìòùáéíóúçñ',
            u'aeiouaeioucn',
        ) :
            word = word.replace(old,new)
        return word

    holidaysSheet = doc.get_worksheet(0)
    holidays2S = table(holidaysSheet,'Vacances2015Semestre2')

    nextFriday = monday+timedelta(days=4)
    mondayYear = monday.year
    startingSemester = 1 if monday < date(mondayYear,7,1) else 2
    startingOffset = (monday - date(mondayYear,1 if startingSemester is 1 else 7,1)).days

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
    with open('indisponibilitats-vacances.conf','w') as holidaysfile:
        for name, days in holidays:
            for day in days:
                holidaysfile.write("{} {} # vacances\n".format(name, day))
    

    step('Baixant altres indisponibilitats setmanals...')

    indisSheet = doc.get_worksheet(5)
    indis = indisSheet.get_all_values()
    with codecs.open('indisponibilitats-setmana.conf','w','utf8') as indisfile:
        for _, who, day, weekday, hours, need, comment in indis[1:] :
            if weekday and day:
                fail("Indisponibilitat especifica dia puntual {} i dia de la setmana {}"
                    .format(day,weekday))
            if weekday.strip():
                fail("Hi ha indisponibilitats permaments al drive, afegeix-les a ma i esborra-les")
            theDay = datetime.datetime.strptime(day, "%d/%m/%Y").date()
            if theDay < iniciSetmana(): continue
            if theDay > iniciSetmana()+timedelta(days=7): continue

            startHours = [ h.split(':')[0].strip() for h in hours.split(',')]
            bitmap = ''.join((
                ('1' if '9' in startHours else '0'),
                ('1' if '10' in startHours else '0'),
                ('1' if '11' in startHours else '0'),
                ('1' if '12' in startHours else '0'),
            ))
            weekdayShort = u'dl dm dx dj dv ds dg'.split()[theDay.weekday()]


            line = u"{} {} {} # {}\n".format(
                transliterate(who),
                weekdayShort,
                bitmap,
                comment)
            indisfile.write(line)

class Backtracker:
	class ErrorConfiguracio(Exception): pass

	def __init__(self, config) :

		self.config = config
		self.globalMaxTurnsADay = config.maximHoresDiariesGeneral
		self.ntelefons = config.nTelefons
		self.dies = config.diesCerca
		self.diesVisualitzacio = config.diesVisualitzacio
		if set(self.dies) != set(self.diesVisualitzacio) :
			raise Backtracker.ErrorConfiguracio(
				"No s'han configurat els mateixos dies per cerca i visualització.")

		self.ndies = len(self.dies)
		self.hores = self.llegeixHores()
		self.nhores = len(self.hores)
		self.torns = self.llegeixTorns('carrega.csv', self.ntelefons)
		self.companys = list(self.torns.keys())
		self.caselles = list(xproduct(self.dies, range(self.nhores), range(self.ntelefons)))
		self.topesDiaris = self.llegeixTopesDiaris(self.companys)
		self.disponible = self.initBusyTable(
            *glob.glob('indisponibilitats*.conf'))

		def createTable(defaultValue, *iterables) :
			"""Creates a table with as many cells as the cross product of the iterables"""
			return dict((keys, defaultValue) for keys in xproduct(*iterables))

		self.teTelefon = createTable(False,  self.dies, range(self.nhores), self.companys)
		self.tePrincipal = createTable(0,  self.companys, self.dies)
		self.horesDiaries = createTable(0,  self.companys, self.dies)

		self.taules = config.taules
		self.telefonsALaTaula = createTable(0,
			self.dies, range(self.nhores), set(self.taules.values()))

		# Number of hours available each day
		self.disponibilitatDiaria = dict(
			((nom,dia), min(
				self.maxTornsDiaris(nom),
				sum(
					0 if self.isBusy(nom,dia,hora) else 1
					for hora in xrange(self.nhores))
				))
			for nom, dia in xproduct(self.companys, self.dies))

		self.grupsAlliberats = dict([
			(company, [
				group 
				for group, companysDelGrup in self.config.sempreUnLliure.items()
				if company in companysDelGrup])
			for company in self.companys
			])

		self.lliuresEnGrupDAlliberats = dict([
			((group, dia, hora), len(companysDelGrup))
			for (group, companysDelGrupa), dia, hora
			in xproduct(
				self.config.sempreUnLliure.items(),
				self.dies,
				xrange(self.nhores),
				)
			])


		self.nbactracks = 0
		self.backtrackDepth = config.backtrackDepth
		self.cutLog = {}

		# just for tracking
		self.bestSolution = []
		self.bestCost = 1000000000

		self.cost = 0
		self.minimumCost = config.costLimit
		self.penalties=[]

		self.ended=False

	def llegeixHores(self):
		lines = [str(h) for h in self.config.hores ]
		return ['-'.join((h1,h2)) for h1,h2 in zip(lines,lines[1:]) ]

	def llegeixTorns(self,tornsfile, ntelefons):
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
			if horesTelefon == self.ndies*self.nhores:
				continue
			raise Backtracker.ErrorConfiguracio(
				"Les hores de T{} sumen {} i no pas {}, revisa {}".format(
					telefon, horesTelefon, self.ndies*self.nhores, tornsfile))
		return result


	def llegeixTopesDiaris(self, persons) :
		dailyMaxPerPerson = dict(
			(nom, int(value))
			for nom, value
			in self.config.maximHoresDiaries.items()
			)
		for name in dailyMaxPerPerson:
			if name in persons: continue
			raise Backtracker.ErrorConfiguracio(
				"Eps, el nom '{}' de maximHoresDiaries a config.yaml no surt a carrega.csv"
				.format(nom))
		return dailyMaxPerPerson

	def maxTornsDiaris(self, company):
		return self.topesDiaris.get(company, self.globalMaxTurnsADay)


	def initBusyTable(self, *filenames) :
		availability = dict(
			((dia,hora,nom), True)
			for nom, dia, hora in xproduct(self.companys, self.dies, range(self.nhores))
			)
		for filename in filenames:
			with open(filename) as thefile:
				for linenum,row in enumerate(thefile) :
					row = row.split('#')[0]
					row = row.split()
					if not row: continue
					row = [col.strip() for col in row]
					company = row[0]
					affectedDays = [row[1]] if row[1] in self.dies else self.dies
					affectedTurns = row[1].strip() if row[1] not in self.dies else (
						row[2] if len(row)>2 else '1'*self.nhores
						)
					if len(affectedTurns)!=self.nhores :
						raise Backtracker.ErrorConfiguracio(
							"'{}':{}: Expected busy string of lenght {} containing '1' on busy hours, found '{}'".format(
							filename, linenum+1, self.nhores, affectedTurns))
					for hora, busy in enumerate(affectedTurns) :
						if busy!='1': continue
						for dia in affectedDays:
							availability[dia, hora, company] = False
		return availability

	def isBusy(self, person, day, hour):
		return not self.disponible[day, hour, person]

	def setBusy(self, person, day, hour, busy=True):
		self.disponible[day, hour, person] = not busy


	def printCuts(self):
		for (depth, motiu), many in sorted(self.cutLog.items()):
			print depth, motiu, many

	def cut(self, motiu, partial):
		try:
			self.cutLog[len(partial), motiu]+=1
		except KeyError:
			self.cutLog[len(partial), motiu]=1
			


	def solve(self) :
		while not self.ended:
			self.nbactracks = 0
			self.solveTorn([])

		self.printCuts()
		if len(self.bestSolution) != len(self.caselles):
			self.minimumCost = self.bestCost
			self.reportSolution((self.bestSolution+['?']*60)[:60] )

	def solveTorn(self, partial):
		if self.ended: return

		if (len(self.bestSolution), -self.bestCost) <= (len(partial), -self.cost):
			print 'Caselles: {}/{} Cost: {}'.format(
                len(partial), len(self.caselles), self.cost)
			self.bestSolution=partial
			self.bestCost=self.cost

		if len(partial) == len(self.caselles):
			self.minimumCost = self.cost
			self.minimumCostReason = self.penalties
			self.reportSolution(partial)
			return

		day, hora, telefon = self.caselles[len(partial)]

		# Comencem dia, mirem si podem acomplir els objectius amb els dies restants
		if not telefon and not hora:

			idia = self.dies.index(day)
			diesRestants =  self.ndies-idia

			# TODO: Heuristica que pot tallar bones solucions
			if self.config.descartaNoPrometedores :
				if idia and self.cost*self.ndies / idia > self.minimumCost:
					self.cut("NoEarlyCost", partial)
					return

			for company in self.companys:
				if self.torns[company][0] > diesRestants * self.config.maximsT1PerDia:
					self.cut("PreveigT1", partial)
#					print "Eps a {} li queden massa T1 per posar".format(company)
					return

				tornsPendents = sum(self.torns[company][torn] for torn in range(self.ntelefons))
				tornsColocables = sum(self.disponibilitatDiaria[company,dia] for dia in self.dies[idia:])
				if tornsPendents > tornsColocables:
					self.cut("PreveigTots", partial)
#					print "Eps a {} nomes li queden {} forats per posar {} hores".format(company, tornsColocables, tornsPendents)
					return
				

		shuffled = list(self.companys)
		if self.config.aleatori:
			random.shuffle(shuffled)

		for company in shuffled:

			cost = 0
			penalties = []
			taula=self.taules[company]

			if self.torns[company][telefon] <= 0:
#				print "{} ja ha exhaurit els seus torns de telefon {}ari".format( company, telefon)
				self.cut("TotColocat", partial)
				continue

			if self.isBusy(company, day, hora):
#				print "{} no esta disponible el {} a la hora {}".format( company, day, hora+1)
				self.cut("Indisponible", partial)
				continue

			if telefon==0 and self.tePrincipal[company, day] >= self.config.maximsT1PerDia:
#				print "Dos principals per {} el {} no, sisplau".format(company,day)
				self.cut("MassesPrincipals", partial)
				continue

			if self.telefonsALaTaula[day, hora, taula]>=self.config.maximPerTaula :
#				print "{} te {} persones a la mateixa taula amb telefon a {}a hora del {}".format(company, self.telefonsALaTaula[day, hora, taula], hora+1, day)
				self.cut("TaulaSorollosa", partial)
				continue

			def lastInIdleGroup():
				for group in self.grupsAlliberats[company] :
					if self.lliuresEnGrupDAlliberats[group, day, hora] > 1:
						continue

#					print "El grup {} on pertany {} no te gent el {} a {} hora".format(group, company, day, hora+1)
					return True
				return False

			def markIdleGroups(company, day, hora):
				for g in self.grupsAlliberats[company] :
					self.lliuresEnGrupDAlliberats[g, day, hora] -= 1
				
			def unmarkIdleGroups(company, day, hora):
				for g in self.grupsAlliberats[company] :
					self.lliuresEnGrupDAlliberats[g, day, hora] += 1
				

			if lastInIdleGroup() or False:
				self.cut("IdleGroupViolated", partial)
				continue

			if self.horesDiaries[company, day] >= self.maxTornsDiaris(company):
#				print "No li posem mes a {} que ja te {} hores el {}".format( company, self.horesDiaries[company], day)
				self.cut("DiaATope", partial)
				continue

			if self.config.deixaEsmorzar and company not in self.config.noVolenEsmorzar:
				if hora==2 and self.teTelefon[day, 1, company]:
#					print "{} es queda sense esmorzar el {}".format(company, day)
					self.cut("Esmorzar", partial)
					continue

			def penalize(value, short, reason):
				penalties.append((value,reason))
				return value

			if hora and self.horesDiaries[company, day] and not self.teTelefon[day, hora-1, company]:
				if self.maxTornsDiaris(company) < 3:
					self.cut("Discontinu", partial)
#					print("{} te hores separades el {}".format(company,day))
					continue

				if self.config.costHoresDiscontinues:
					cost += penalize(self.config.costHoresDiscontinues, "Discontinu",
						"{} te hores separades el {}".format(company, day))

			if self.horesDiaries[company, day]>0 :
				cost += penalize(
					self.config.costHoresConcentrades * self.horesDiaries[company, day],
					"Repartiment",
					"{} te mes de {} hores el {}".format(company, self.horesDiaries[company, day], day))

			if self.telefonsALaTaula[day, hora, taula]>0 :
				cost += penalize(
					self.config.costTaulaSorollosa * self.telefonsALaTaula[day, hora, taula],
					"Ocupacio",
					"{} te {} persones a la mateixa taula amb telefon a {}a hora del {}".format(
						company, self.telefonsALaTaula[day, hora, taula], hora+1, day))

			if self.cost + cost > self.minimumCost :
#				print "Solucio masa costosa: {}".format(self.cost+cost)
				self.cut("TooMuchCost", partial)
				break

			if self.cost + cost == self.minimumCost and len(partial)<len(self.caselles)*0.7 :
#				print "Solucio segurament massa costosa, no perdem temps: {}".format(self.cost+cost)
				self.cut("CostEqual", partial)
				break

			if self.config.mostraCami:
				if len(partial) < self.config.maximCamiAMostrar :
					print "  "*len(partial)+company[:2]

			# Anotem la casella
			self.cost += cost
			self.penalties += penalties
			if telefon == 0: self.tePrincipal[company, day]+=1
			self.teTelefon[day, hora, company]=True
			self.setBusy(company,day,hora)
			self.horesDiaries[company,day]+=1
			self.torns[company][telefon]-=1
			self.telefonsALaTaula[day,hora,taula]+=1
			markIdleGroups(company,day,hora)

			# Provem amb la seguent casella
			self.solveTorn(partial+[company])
			self.nbactracks += 1

			# Desanotem la casella
			unmarkIdleGroups(company,day,hora)
			self.telefonsALaTaula[day,hora,taula]-=1
			self.torns[company][telefon]+=1
			self.horesDiaries[company,day]-=1
			self.setBusy(company,day,hora, False)
			self.teTelefon[day, hora, company]=False
			if telefon == 0: self.tePrincipal[company, day]-=1
			if penalties:
				del self.penalties[-len(penalties):]
			self.cost -= cost

			# Si portem massa estona explorant el camí parem i provem un altre
			if self.config.aleatori and self.nbactracks > self.backtrackDepth: break

	def reportSolution(self, solution) :

		# buidar el fitxer, si el cost es diferent
		monday = iniciSetmana()

		firstAtCost = self.minimumCost != self.__dict__.get('storedCost', 'resEsComparaAmbMi')
		if firstAtCost:
			self.storedCost = self.minimumCost
			header = ("""\
<!doctype html>
<html>
<head>
<meta charset='utf-8' />
<style>
h1 {
    color: #560;
}
td, th {
	border:1px solid black;
	width: 8em;
	text-align: center;
}
td:empty { border:0;}
td { padding: 1ex;}
"""+ ''.join(
				(".{} {{ background-color: #{:01x}{:02x}{:02x}; }}\n".format(
							nom, random.randint(127,255), random.randint(127,255), random.randint(127,255)) for nom in self.companys)
				if self.config.randomColors else
				(".{} {{ background-color: #{}; }}\n".format(
							nom, self.config.colors[nom]) for nom in self.companys)
				)
					+"""
</style>
</head>
<body>
""")
			with open("graella-telefons-{}.html".format(monday),'w') as output:
				output.write(header)
				output.write("<h1>Setmana {}</h1>".format(monday))
			with open("taula.html",'w') as output:
				output.write(header)

		solution = dict(zip(self.caselles, solution))
		taula = '\n'.join(
				[
					'<table>',
					'<tr><td></td><th colspan=3>' +
					'</th><td></td><th colspan=3>'.join(
						d for d in self.diesVisualitzacio
					) + '</th><tr>',
					'<tr><td></td>' +
					'\n<td></td>\n'.join(
						''.join(
							'<th>T{}</th>'.format(telefon+1)
							for telefon in range(self.ntelefons))
						+ '\n'
						for d in self.diesVisualitzacio
					) + '<tr>',
				]+
				[
					'<tr><th>{}</th>\n'.format(h) +
					'\n<td>&nbsp;</td>\n'.join(
						'\n'.join(
							"<td class='{0}'>{1}</td>".format(
								solution[d,hi,l].lower(),
								solution[d,hi,l].capitalize()
								) for l in range(self.ntelefons)
							) for d in self.diesVisualitzacio)
					+ '\n</tr>'
					for hi, h in enumerate(self.hores)
				]
				+ [
					'</table>',
				]
			)
		penalitzacions = '\n'.join([
					"",
					"<p>Penalitzacio: {}</p>".format(self.minimumCost),
					"<ul>",
					"\n".join(
						"<li>{}: {}</li>".format(*reason)
						for reason in self.penalties
					),
					"</ul>",
					'',
				])
		with open("taula.html",'a') as output:
			output.write(taula)
			output.write(penalitzacions)
		if firstAtCost:
			with open("graella-telefons-{}.html".format(monday),'a') as output:
				output.write(taula)
				output.write('\n'.join([
                    '',
					'</body>',
					'</head>',
                    '',
					]))

#		exit(0)


import sys

if '--keep' in sys.argv:
	sys.argv.remove('--keep')
else:
	baixaDades(iniciSetmana())

import signal
import subprocess

def signal_handler(signal, frame):
	print 'You pressed Ctrl-C!'
	b.ended = True

signal.signal(signal.SIGINT, signal_handler)

from namespace import namespace as ns

step('Carregant configuració...')
try:
    b = Backtracker(ns.load("config.yaml"))
except:
    error("Configuració incorrecta")
    raise

step('Generant horari...')
b.solve()







