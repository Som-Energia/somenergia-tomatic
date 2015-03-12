#!/usr/bin/env python

import itertools
import random

def llegeixHores(horesfile):
	linees = [
		l.strip() for l in open(horesfile) if l.strip() ]
	return ['-'.join((h1,h2)) for h1,h2 in zip(linees,linees[1:]) ]

def llegeixTorns(tornsfile):
	return dict(
		(nom, [int(primer), int(segon), int(tercer)])
		for nom, primer, segon, tercer in (
			line.split("\t")
			for line in open(tornsfile)
			)
		)
def llegeixDisponibilitat(disponibilitatFile):
	with open(disponibilitatFile) as thefile:
		return[
			(
				row[0],
				row[1] if row[1] in dies else None,
				row[1] if row[1] not in dies else (row[2] if len(row)>2 else None)
			)
			for row in ( line.split() for line in thefile)
		]

torns = llegeixTorns('torns.csv')
hores=llegeixHores('hores.csv')
nhores=len(hores)
nnivells=3
dies = 'dl','dm','dx','dj','dv'
ndies=len(dies)
indisponibilitats = llegeixDisponibilitat('indisponibilitats.conf')


caselles = list(itertools.product(dies, range(nhores), range(nnivells)))

class Backtracker:
	def __init__(self, shuffle=True) :
		self.doshuffle=shuffle
		self.companys = list(torns.keys())
		self.disponible = dict((
			((dia,hora,nom), not self.indisponible(dia, hora, nom))
			for nom, dia, hora in itertools.product(self.companys, dies, range(nhores))
			))
		self.teTelefon = dict((
			((dia,hora,nom), False)
			for nom, dia, hora in itertools.product(self.companys, dies, range(nhores))
			))
		self.tePrincipal = dict((
			((nom, dia), False)
			for nom, dia in itertools.product(self.companys, dies)
			))
		self.horesDiaries = dict(((nom,dia), 0) for nom,dia in itertools.product(self.companys,dies))
		self.nbactracks = 0

	def solve(self) :
		while True:
			self.nbactracks = 0
			self.solveTorn([])

	def indisponible(self, dia, hora, company) :
		for acompany, adia, ahora in indisponibilitats:
			if company != acompany: continue
			if adia is not None and dia != adia: continue
			if ahora is not None and ahora[hora] == '0': continue
			return True
		return False


	def solveTorn(self, partial):
		if len(partial) == len(caselles):
			self.reportSolution(partial)
			return
		day, hora, nivell = caselles[len(partial)]

		if not nivell and not hora:
			# Comencem dia
			diesRestants =  5-dies.index(day)
			tornsColocables = diesRestants*2
			for company in self.companys:
				if torns[company][0] > diesRestants:
					print "Eps a {} li queden massa T1 per posar".format(company)
					return
				tornsPendents = sum(torns[company][torn] for torn in range(nnivells))
				if tornsPendents > tornsColocables:
#					print "Eps a {} no li queden dies per posar les seves hores".format(company)
					return

		companys = list(torns.keys())
		if self.doshuffle:
			random.shuffle(companys)

		for company in companys:
			if torns[company][nivell] < 1:
#				print "En {} ja ha exhaurit els seus torns de {} nivell".format( company, nivell)
				continue
			if not self.disponible[day, hora, company]:
#				print "En {} no esta disponible el {} a la hora {}".format( company, day, hora)
				continue
			if self.horesDiaries[company, day]==2:
#				print "No li posem mes a {} que ja te {} hores el {}".format( company, self.horesDiaries[company], day)
				continue
			if hora and self.horesDiaries[company, day] and not self.teTelefon[day, hora-1, company]:
#				print "No li posem hores trencades a {} el {}".format(company, day)
				continue
			if hora==2 and self.teTelefon[day, hora-1, company]==1:
#				print "Deixem esmorzar a {} el {}".format( company, day)
				continue
			if nivell==0 and self.tePrincipal[company, day]:
#				print "Dos principals al {} el {} no, sisplau".format(company,day)
				continue

			if len(partial) < 60 : print "  "*len(partial)+company[:2]

			if nivell == 0: self.tePrincipal[company, day]=True
			self.teTelefon[day, hora, company]=True
			self.disponible[day, hora, company]=False
			self.horesDiaries[company,day]+=1
			torns[company][nivell]-=1

			self.solveTorn(partial+[company])
			self.nbactracks += 1

			torns[company][nivell]+=1
			self.horesDiaries[company,day]-=1
			self.disponible[day, hora, company]=True
			self.teTelefon[day, hora, company]=False
			if nivell == 0: self.tePrincipal[company, day]=False

			if self.nbactracks > 100000:
				break
			

	def reportSolution(self, solution) :
		solution = dict(zip(caselles, solution))
		with open("taula.html",'w') as output:
			output.write("""\
	<style>
	td, th {
		border:1px solid black;
		width: 8em;
		text-align: center;
	}
	td { padding: 1ex;}
	"""+ ''.join(".{} {{ background-color: #{:02x}{:02x}{:02x}; }}\n".format(
		nom, random.randint(127,255), random.randint(127,255), random.randint(127,255)) for nom in self.companys)
	+""")
	</style>
			""")
			output.write( '\n'.join(
				[
					'<table>',
					'<tr><td></td><th colspan=3>' + '</th><td></td><th colspan=3>'.join(
						dia for dia in dies
					) + '</th><tr>',
					'<tr><td></td><th>' + 
					'<th>'.join(
						'</th><th>'.join(
							'T{}'.format(nivell+1)
							for nivell in range(nnivells))+'</th><td></td>'
						for dia in dies
					) + '</th><tr>',
				]+
				[
					'<tr><th>{}</th>'.format(h) +
					'<td>&nbsp;</td>'.join(
						'</td>'.join("<td class='{0}'>{0}</td>".format(solution[d,hi,l]) for l in range(nnivells))
						for d in dies)
					+ '</tr>'
					for hi, h in enumerate(hores)
				]
				+ ['</table>']
				))
		exit(0)

b = Backtracker()
b.solve()







