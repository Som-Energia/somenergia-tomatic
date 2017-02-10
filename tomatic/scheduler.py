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
from sheetfetcher import SheetFetcher
from tomatic.htmlgen import HtmlGenFromSolution

# Dirty Hack: Behave like python3 open regarding unicode
def open(*args, **kwd):
	return codecs.open(encoding='utf8', *args, **kwd)

def transliterate(word):
	word=unicode(word).lower()
	for old, new in zip(
		u'àèìòùáéíóúçñ',
		u'aeiouaeioucn',
	) :
		word = word.replace(old,new)
	return word

def baixaDades(config, certificat) :

	def table(sheet, name):
		cells = sheet.range(name)
		width = cells[-1].col-cells[0].col +1
		height = cells[-1].row-cells[0].row +1
		return [ 
			[cell.value for cell in row]
			for row in zip( *(iter(cells),)*width)
			]


	step('Autentificant al Google Drive')
	fetcher = SheetFetcher(
		documentName='Quadre de Vacances',
		credentialFilename=certificat,
		)

	step('Baixant carrega setmanal...')

	carregaRangeName = config.intervalCarrega.format(
		*config.monday.timetuple())
	step("  Descarregant el rang '{}'...".format(carregaRangeName))
	carrega = fetcher.get_range(config.fullCarrega, carregaRangeName)
	step("  Guardant-ho com '{}'...".format('carrega.csv'))
	with open('carrega.csv','w') as phoneload :
		phoneload.write(
			"\n".join(
				'\t'.join(c for c in row)
				for row in carrega
				)
			)

	step('Baixant vacances...')

	nextFriday = config.monday+timedelta(days=4)
	mondayYear = config.monday.year
	startingSemester = 1 if config.monday < date(mondayYear,7,1) else 2
	startingOffset = (config.monday - date(mondayYear,1 if startingSemester is 1 else 7,1)).days

	holidays2SRange = 'Vacances{}Semestre{}'.format(
		mondayYear,
		startingSemester,
		)
	step("  Baixant vacances de l'interval {}".format(holidays2SRange))
	holidays2S = fetcher.get_range(str(mondayYear), holidays2SRange)

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
				holidaysfile.write("{} {} # vacances\n".format(name, day))


	step("Baixant altres indisponibilitats setmanals...")

	step("  Baixant el full '{}'...".format(config.fullIndisponibilitats))
	indis = fetcher.get_fullsheet(config.fullIndisponibilitats)
	step("  Guardant indisponibilitats setmanals a 'indisponibilitats-setmana.conf'...")
	with open('indisponibilitats-setmana.conf','w') as indisfile:
		for _, who, day, weekday, hours, need, comment in indis[1:] :
			if weekday and day:
				fail("Indisponibilitat especifica dia puntual {} i dia de la setmana {}"
					.format(day,weekday))
			if weekday.strip():
				fail("Hi ha indisponibilitats permaments al drive, afegeix-les a ma i esborra-les")
			theDay = datetime.datetime.strptime(day, "%d/%m/%Y").date()
			if theDay < config.monday: continue
			if theDay > config.monday+timedelta(days=6): continue

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
		self.outputFile = "graella-telefons-{}.html".format(config.monday)
		self.outputYaml = "graella-telefons-{}.yaml".format(config.monday)
		self.globalMaxTurnsADay = config.maximHoresDiariesGeneral
		self.ntelefons = config.nTelefons
		self.dies = config.diesCerca
		self.diesVisualitzacio = config.diesVisualitzacio
		diesErronis = set(self.dies) - set(self.diesVisualitzacio)
		if diesErronis:
			raise Backtracker.ErrorConfiguracio(
				"Aquests dies no son a la llista de visualitzacio: {}".format(diesErronis))

		self.ndies = len(self.dies)
		self.hours = self.llegeixHores()
		self.nhours = len(self.hours)
		self.torns = self.llegeixTorns('carrega.csv', self.ntelefons)
		self.companys = list(self.torns.keys())
		self.caselles = list(xproduct(self.dies, range(self.nhours), range(self.ntelefons)))
		self.topesDiaris = self.llegeixTopesDiaris(self.companys)
		self.disponible = self.initBusyTable(
			*glob.glob('indisponibilitats*.conf'))

		def createTable(defaultValue, *iterables) :
			"""Creates a table with as many cells as the cross product of the iterables"""
			return dict((keys, defaultValue) for keys in xproduct(*iterables))

		self.teTelefon = createTable(False,  self.dies, range(self.nhours), self.companys)
		self.tePrincipal = createTable(0,  self.companys, self.dies)
		self.horesDiaries = createTable(0,  self.companys, self.dies)

		self.taules = config.taules
		self.telefonsALaTaula = createTable(0,
			self.dies, range(self.nhours), set(self.taules.values()))

		# Number of hours available each day
		self.disponibilitatDiaria = dict(
			((nom,dia), min(
				self.maxTornsDiaris(nom),
				sum(
					0 if self.isBusy(nom,dia,hora) else 1
					for hora in xrange(self.nhours))
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
				xrange(self.nhours),
				)
			])


		self.nbactracks = 0
		self.backtrackDepth = config.backtrackDepth
		self.cutLog = {}
		self.deeperCutDepth = 0
		self.deeperCutLog = None

		# just for tracking
		self.bestSolution = []
		self.bestCost = 1000000000

		self.cost = 0
		self.minimumCost = config.costLimit
		self.penalties=[]

		self.terminated=False

	def llegeixHores(self):
		lines = [str(h) for h in self.config.hours ]
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
			if horesTelefon == self.ndies*self.nhours:
				continue
			raise Backtracker.ErrorConfiguracio(
				"Les hores de T{} sumen {} i no pas {}, revisa {}".format(
					telefon+1, horesTelefon, self.ndies*self.nhours, tornsfile))
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
				"El nom '{}' de maximHoresDiaries a config.yaml no surt a carrega.csv"
				.format(name))
		return dailyMaxPerPerson

	def maxTornsDiaris(self, company):
		return self.topesDiaris.get(company, self.globalMaxTurnsADay)


	def initBusyTable(self, *filenames) :
		availability = dict(
			((dia,hora,nom), True)
			for nom, dia, hora in xproduct(self.companys, self.dies, range(self.nhours))
			)
		for filename in filenames:
			with open(filename) as thefile:
				for linenum,row in enumerate(thefile) :
					row = row.split('#')[0]
					row = row.split()
					if not row: continue
					row = [col.strip() for col in row]
					company = row[0]
					affectedDays = self.dies
					remain = row[1:]
					if row[1] in self.diesVisualitzacio:
						if row[1] not in self.dies: # holyday
							continue
						affectedDays = [row[1]]
						remain = row[2:]
					affectedTurns = remain[0].strip() if remain else '1'*self.nhours

					if len(affectedTurns)!=self.nhours :
						raise Backtracker.ErrorConfiguracio(
							"'{}':{}: Expected busy string of lenght {} "
							"containing '1' on busy hours, found '{}'".format(
							filename, linenum+1, self.nhours, affectedTurns))
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

	def cut(self, motiu, partial, log=None):
		try:
			self.cutLog[len(partial), motiu]+=1
		except KeyError:
			self.cutLog[len(partial), motiu]=1
		if motiu in args.verbose:
			warn(log or motiu)
		if self.deeperCutLog and len(self.deeperCutLog) > len(partial): return
		self.deeperCutDepth = len(partial)
		self.deeperCutLog = log or motiu
		


	def solve(self) :
		while not self.terminated:
			self.nbactracks = 0
			self.solveTorn([])
			if self.nbactracks < self.backtrackDepth:
				break

		ncaselles = len(self.caselles)

		if len(self.bestSolution) != ncaselles:
			self.printCuts()
			self.minimumCost = self.bestCost
			self.reportSolution((self.bestSolution+['?']*ncaselles)[:ncaselles] )
			error("Impossible trobar solució\n{}".format( self.deeperCutLog))
		else:
			step("Millor graella grabada a '{}'".format(self.outputFile))
			step("Millor graella grabada a '{}'".format(self.outputYaml))

	def solveTorn(self, partial):
		if self.terminated: return

		# Better solution found? Report and hold it
		# A more complete solution is always better
		if (len(self.bestSolution), -self.bestCost) <= (len(partial), -self.cost):
			if len(partial) == len(self.caselles):
				print 'Solució trobada amb cost {}.'.format(self.cost)
			else:
				print 'Solució incomplerta {}/{} caselles, cost {}'.format(
					len(partial), len(self.caselles), self.cost)
			self.bestSolution=partial
			self.bestCost=self.cost

		# Complete solution? Stop backtracking.
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
					self.cut("NoEarlyCost", partial,
						"Tallant una solucio poc prometedora")
					return

			for company in self.companys:
				if self.torns[company][0] > diesRestants * self.config.maximsT1PerDia:
					self.cut("T1RestantsIncolocables", partial,
						"A {} li queden massa T1 per posar"
						.format(company))
					return

				tornsPendents = sum(
					self.torns[company][torn]
					for torn in range(self.ntelefons)
					)
				tornsColocables = sum(
					self.disponibilitatDiaria[company,dia]
					for dia in self.dies[idia:]
					)
				if tornsPendents > tornsColocables:
					self.cut("RestantsIncolocables", partial,
						"A {} nomes li queden {} forats per posar {} hores"
						.format(company, tornsColocables, tornsPendents))
					return

		companys = list(self.companys)
		if self.config.aleatori:
			random.shuffle(companys)

		if (day, hora+1, telefon+1) in self.config.forced:
			companys = [self.config.forced[(day,hora+1,telefon+1)]]

		for company in companys:

			cost = 0
			penalties = []
			taula=self.taules[company]

			# Motius de rebuig del camí

			if self.torns[company][telefon] <= 0:
				self.cut("TotColocat", partial,
					"{} ja ha exhaurit els seus torns de telefon {}ari"
					.format( company, telefon))
				continue

			if self.isBusy(company, day, hora):
				self.cut("Indisponible", partial,
					"{} no esta disponible el {} a la hora {}"
					.format( company, day, hora+1))
				continue

			if telefon==0 and self.tePrincipal[company, day] >= self.config.maximsT1PerDia:
				self.cut("MassesPrincipals", partial,
					"Dos principals per {} el {} no, sisplau"
					.format(company,day))
				continue

			if self.telefonsALaTaula[day, hora, taula]>=self.config.maximPerTaula :
				self.cut("TaulaSorollosa", partial,
					"{} ja té {} persones a la mateixa taula amb telefon a {}a hora del {}"
					.format(company, self.telefonsALaTaula[day, hora, taula], hora+1, day))
				continue

			def lastInIdleGroup():
				for group in self.grupsAlliberats[company] :
					if self.lliuresEnGrupDAlliberats[group, day, hora] > 1:
						continue

					return ("El grup {} on pertany {} no te gent el {} a {} hora"
						.format(group, company, day, hora+1))
				return False

			def markIdleGroups(company, day, hora):
				for g in self.grupsAlliberats[company] :
					self.lliuresEnGrupDAlliberats[g, day, hora] -= 1
				
			def unmarkIdleGroups(company, day, hora):
				for g in self.grupsAlliberats[company] :
					self.lliuresEnGrupDAlliberats[g, day, hora] += 1
				

			if lastInIdleGroup():
				self.cut("IdleGroupViolated", partial, lastInIdleGroup())
				continue

			if self.horesDiaries[company, day] >= self.maxTornsDiaris(company):
				self.cut("DiaATope", partial,
					"No li posem mes a {} que ja te {} hores el {}"
					.format( company, self.horesDiaries[company, day], day))
				continue

			if self.config.deixaEsmorzar and company not in self.config.noVolenEsmorzar:
				if hora==2 and self.teTelefon[day, 1, company]:
					self.cut("Esmorzar", partial,
						"{} es queda sense esmorzar el {}"
						.format(company, day))
					continue

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
				self.cut("TooMuchCost", partial,
					"Solucio masa costosa: {}"
					.format(self.cost+cost))
				break

			if self.cost + cost == self.minimumCost and len(partial)<len(self.caselles)*0.7 :
				self.cut("CostEqual", partial,
					"Solucio segurament massa costosa, no perdem temps: {}"
					.format(self.cost+cost))
				break

			if self.config.mostraCami or args.track:
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
		def properName(name):
			"""Capitalizes name unless configuration provides
			A better alternative, for example with tildes.
			"""
			return self.config.noms.get(name, name.title())

		firstAtCost = self.minimumCost != self.__dict__.get('storedCost', 'resEsComparaAmbMi')
		solution = dict(zip(self.caselles, solution))
		htmlgen=HtmlGenFromSolution(self.config,solution,self.config.monday)
		if firstAtCost:
			# Is the first that good, start from scratch
			self.storedCost = self.minimumCost
			personalColors = htmlgen.htmlColors()
			header = htmlgen.htmlHeader()
			subheader = htmlgen.htmlSubHeader()
			htmlgen.getYaml().dump(self.outputYaml)
			with open(self.outputFile,'w') as output:
				output.write(
					header+personalColors+
					subheader+
					htmlgen.htmlSetmana())
			with open(self.config.monitoringFile,'w') as output:
				output.write(
					header+personalColors+
					subheader
				)

		solution = dict(zip(self.caselles, solution))
		penalitzacions = (
			htmlgen.htmlPenalizations(
				self.minimumCost,
				self.penalties)
		)
		with open(self.config.monitoringFile,'a') as output:
			output.write(htmlgen.htmlTable())
			output.write(penalitzacions)
		if firstAtCost:
			htmlgen.getYaml().dump(self.outputYaml)
			with open(self.outputFile,'a') as output:
				output.write(htmlgen.htmlTable()+
					htmlgen.htmlExtensions()+
					htmlgen.htmlFixExtensions()+
					htmlgen.htmlFooter())



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
		dest='verbose',
		metavar='message',
		nargs='+',
		default=[],
		help="activa els missatges de tall del tipus indicat",
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

	return parser.parse_args()

args=None

def main():
	global args
	import sys

	args = parseArgs()

	step('Carregant configuració...')
	from yamlns import namespace as ns
	try:
		config = ns.load("config.yaml")
	except:
		error("Configuració incorrecta")
		raise

	if args.date is not None:
		# take the monday of the week including that date
		givenDate = datetime.datetime.strptime(args.date,"%Y-%m-%d").date()
		config.monday = givenDate - timedelta(days=givenDate.weekday())
	else:
		# If no date provided, take the next monday
		today = date.today()
		config.monday = today + timedelta(days=7-today.weekday())

	if not args.keep:
		baixaDades(config, args.certificate)

	import signal
	import subprocess

	def signal_handler(signal, frame):
		print 'You pressed Ctrl-C!'
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



# vim: noet
