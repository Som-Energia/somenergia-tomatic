#!/usr/bin/env python


torns = dict(
	(nom, [int(primer), int(segon), int(tercer)])
	for nom, primer, segon, tercer in (
		line.split("\t")
		for line in open('torns.csv')
		)
	)

print torns

indisponibilitats = [
	('tania','dl',None),
	('erola',None,'1000'),
	('judit','dl',None),
	('pere',None,'1000'),
	('marc',None,'1000'),
	('david',None,'1100'),
	('david','dl',None),
	]

dies = 'dl','dm','dx','dj','dv'

import itertools

nhores=4
nnivells=3

caselles = list(itertools.product(dies, range(nhores), range(nnivells)))

import random

class Backtracker:
	def __init__(self, shuffle=True) :
		self.doshuffle=shuffle
		self.companys = list(torns.keys())
		self.disponible = dict((
			((dia,hora,nom), not self.indisponible(dia, hora, nom))
			for nom, dia, hora in itertools.product(self.companys, dies, range(nhores))
			))

	def solve(self) :
		return self.solveTorn([])

	def indisponible(self, dia, hora, company) :
		for acompany, adia, ahora in indisponibilitats:
			if company != acompany: continue
			if adia is not None and dia != adia: continue
			if ahora is not None and ahora[hora] == '0': continue
			return True
		return False

	def hasOnDay(self, partial, company, day):
		day = dies.index(day)
		turns = partial[day*nhores*nnivells:(day+1)*nhores*nnivells]
		return len([c for c in turns if c==company])>2


	def solveTorn(self, partial):
		if len(partial) == len(caselles):
			print(partial)
			return
		day, hora, nivell = caselles[len(partial)]
#		print day,hora,nivell, partial
		companys = list(torns.keys())
		if self.doshuffle:
			random.shuffle(companys)
		for company in companys:
			if torns[company][nivell] == 0:
#				print "En {} ja ha exhaurit els seus torns de {} nivell".format(company, nivell)
				continue
			if not self.disponible[day, hora, company]:
#				print "En {} no esta disponible el {} a la hora {}".format(company, day, hora)
				continue
			if self.hasOnDay(partial, company, day):
#				print "En {} ja te massa hores el {}".format(company, day)
				continue
			self.disponible[day, hora, company]=False
			torns[company][nivell]-=1
			self.solveTorn(partial+[company])
			torns[company][nivell]+=1
			self.disponible[day, hora, company]=True


b = Backtracker()
b.solve()







