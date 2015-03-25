#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import product as xproduct
import random

class Backtracker:
	class ErrorConfiguracio(Exception): pass

	def __init__(self, config) :

		self.config = config
		self.verboseSteps = config.mostraCami
		self.globalMaxTurnsADay = config.maximHoresDiariesGeneral
		self.doshuffle = config.aleatori
		self.ntelefons = config.nTelefons
		self.dies = config.diesCerca
		self.diesVisualitzacio = config.diesVisualitzacio
		if set(self.dies) != set(self.diesVisualitzacio) :
			raise Backtracker.ErrorConfiguracio(
				"No s'han configurat els mateixos dies per cerca i visualització.")

		self.ndies = len(self.dies)
		self.hores = self.llegeixHores()
		self.nhores = len(self.hores)
		self.torns = self.llegeixTorns('torns.csv', self.ntelefons)
		self.companys = list(self.torns.keys())
		self.caselles = list(xproduct(self.dies, range(self.nhores), range(self.ntelefons)))
		self.topesDiaris = self.llegeixTopesDiaris('topesDiaris.csv', self.companys)
		self.disponible = self.initBusyTable(
			'indisponibilitats.conf', self.companys, self.dies, self.nhores)

		self.teTelefon = dict((
			((dia,hora,nom), False)
			for nom, dia, hora in xproduct(self.companys, self.dies, range(self.nhores))
			))
		self.tePrincipal = dict((
			((nom, dia), 0)
			for nom, dia in xproduct(self.companys, self.dies)
			))
		self.horesDiaries = dict(
			((nom,dia), 0)
			for nom, dia in xproduct(self.companys, self.dies))

		# Number of hours available each day
		self.disponibilitatDiaria = dict(
			((nom,dia), min(
				self.maxTornsDiaris(nom),
				sum(
					0 if self.isBusy(nom,dia,hora) else 1
					for hora in xrange(self.nhores))
				))
			for nom, dia in xproduct(self.companys, self.dies))

		self.taules = config.taules

		self.ocupacioTaules = dict(
			((dia, hora, taula), 0)
			for dia, hora, taula in xproduct(self.dies, range(self.nhores), set(self.taules.values())))

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


	def llegeixTopesDiaris(self, filename, persons) :
		dailyMaxPerPerson = dict(
			(nom, int(value))
			for nom, value
			in self.config.maximHoresDiaries.items()
			)
		for name in dailyMaxPerPerson:
			if name in persons: continue
			raise Backtracker.ErrorConfiguracio(
				"Eps, el nom '{}' de maximHoresDiaries a config.yaml no surt a torns.csv"
				.format(nom))
		return dailyMaxPerPerson

	def maxTornsDiaris(self, company):
		return self.topesDiaris.get(company, self.globalMaxTurnsADay)


	def initBusyTable(self, filename, companys, dies, nhores) :
		availability = dict(
			((dia,hora,nom), True)
			for nom, dia, hora in xproduct(companys, dies, range(nhores))
			)
		with open(filename) as thefile:
			for linenum,row in enumerate(line.split() for line in thefile) :
				if not row: continue
				row = [col.strip() for col in row]
				company = row[0]
				affectedDays = [row[1]] if row[1] in dies else dies
				affectedTurns = row[1].strip() if row[1] not in dies else (
					row[2] if len(row)>2 else '1'*nhores
					)
				if len(affectedTurns)!=nhores :
					raise Backtracker.ErrorConfiguracio(
						"'{}':{}: Expected busy string of lenght {} containing '1' on busy hours, found '{}'".format(
						filename, linenum+1, nhores, affectedTurns))
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
			self.bestSolution=partial
			self.bestCost=self.cost
			print len(partial), self.cost

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
		if self.doshuffle:
			random.shuffle(shuffled)

		for company in shuffled:

			cost = 0
			penalties = []
			taula=self.taules[company]

			if self.torns[company][telefon] < 1:
#				print "{} ja ha exhaurit els seus torns de {} telefon".format( company, telefon)
				self.cut("TotColocat", partial)
				continue

			if self.isBusy(company, day, hora):
#				print "{} no esta disponible el {} a la hora {}".format( company, day, hora+1)
				self.cut("Indisponible", partial)
				continue

			if telefon==0 and self.tePrincipal[company, day] >= self.config.maximsT1PerDia:
#				print "Dos principals per {} el {} no, sisplau".format(company,day)
				self.cut("DosPrincipals", partial)
				continue

			if self.ocupacioTaules[day, hora, taula]>=self.config.maximPerTaula :
#				print "{} te {} persones a la mateixa taula amb telefon a {}a hora del {}".format(company, self.ocupacioTaules[day, hora, taula], hora+1, day)
				self.cut("TaulaSorollosa", partial)
				continue

			if self.horesDiaries[company, day] >= self.maxTornsDiaris(company):
#				print "No li posem mes a {} que ja te {} hores el {}".format( company, self.horesDiaries[company], day)
				self.cut("DiaATope", partial)
				continue

			if hora==2 and self.teTelefon[day, 1, company]:
#				print "{} es queda sense esmorzar el {}".format(company, day)
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

				cost += penalize(40, "Discontinu",
					"{} te hores separades el {}".format(company, day))

			if self.horesDiaries[company, day]>0 :
				cost += penalize(self.horesDiaries[company, day], "Repartiment",
					"{} te mes de {} hores el {}".format(company, self.horesDiaries[company, day], day))

			if self.ocupacioTaules[day, hora, taula]>0 :
				cost += penalize(self.ocupacioTaules[day, hora, taula]*5, "Ocupacio",
					"{} te {} persones a la mateixa taula amb telefon a {}a hora del {}".format(
						company, self.ocupacioTaules[day, hora, taula], hora+1, day))

			if self.cost + cost > self.minimumCost :
#				print "Solucio masa costosa: {}".format(self.cost+cost)
				self.cut("TooMuchCost", partial)
				break

			if self.cost + cost == self.minimumCost and len(partial)<len(self.caselles)*0.7 :
#				print "Solucio segurament massa costosa, no perdem temps: {}".format(self.cost+cost)
				self.cut("CostEqual", partial)
				break

			self.cost += cost
			self.penalties += penalties

			if self.verboseSteps and len(partial) < 60 :
				print "  "*len(partial)+company[:2]

			if telefon == 0: self.tePrincipal[company, day]+=1
			self.teTelefon[day, hora, company]=True
			self.setBusy(company,day,hora)
			self.horesDiaries[company,day]+=1
			self.torns[company][telefon]-=1
			self.ocupacioTaules[day,hora,taula]+=1

			self.solveTorn(partial+[company])
			self.nbactracks += 1

			self.ocupacioTaules[day,hora,taula]-=1
			self.torns[company][telefon]+=1
			self.horesDiaries[company,day]-=1
			self.setBusy(company,day,hora, False)
			self.teTelefon[day, hora, company]=False
			if telefon == 0: self.tePrincipal[company, day]-=1
			if penalties:
				del self.penalties[-len(penalties):]
			self.cost -= cost

			if self.nbactracks > self.backtrackDepth: break

	def reportSolution(self, solution) :

		# buidar el fitxer, si el cost es diferent
		if self.minimumCost != self.__dict__.get('storedCost', 'resEsComparaAmbMi'):
			with open("taula.html",'w') as output:
				self.storedCost = self.minimumCost
				output.write("""\
<!doctype html>
<html>
<head>
<style>
td, th {
	border:1px solid black;
	width: 8em;
	text-align: center;
}
td:empty { border:0;}
td { padding: 1ex;}
"""+ ''.join(
			".{} {{ background-color: #{:02x}{:02x}{:02x}; }}\n".format(
						nom, random.randint(127,255), random.randint(127,255), random.randint(127,255)) for nom in self.companys)
					+"""
</style>
</head>
<body>
""")

		solution = dict(zip(self.caselles, solution))
		with open("taula.html",'a') as output:
			output.write( '\n'.join(
				[
					'<table>',
					'<tr><td></td><th colspan=3>' +
					'</th><td></td><th colspan=3>'.join(
						d for d in self.diesVisualitzacio
					) + '</th><tr>',
					'<tr><td></td>' +
					''.join(
						''.join(
							'<th>T{}</th>'.format(telefon+1)
							for telefon in range(self.ntelefons))
						+ '\n<td></td>\n'
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
					"<p>Penalitzacio: {}</p>".format(self.minimumCost),
					"<ul>",
					"\n".join(
						"<li>{}: {}</li>".format(*reason)
						for reason in self.penalties
					),
					"</ul>",
					'',
				]
				))
#		exit(0)


import sys
import unittest

class Backtracker_Test(unittest.TestCase):
	def test_availability(self):
		availability = initBusyTable()

if '--test' in sys.argv:
	sys.argv.remove('--test')
	unittest.main()

import signal
import subprocess

def signal_handler(signal, frame):
	print 'You pressed Ctrl-C!'
	b.ended = True

signal.signal(signal.SIGINT, signal_handler)

from namespace import namespace as ns

b = Backtracker(ns.load("config.yaml"))
b.solve()







