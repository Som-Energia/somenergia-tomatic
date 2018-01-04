#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from . import busy
from yamlns import namespace as ns
import datetime

def isodate(datestr):
	return datetime.datetime.strptime(datestr, "%Y-%m-%d").date()


config = ns.load("config.yaml")
twoHours = ['05/07/2017 14:51:14', 'WorkMate1', '11/07/2017', '', '11:30 - 12:45, 12:45 - 14:00', u'Necess\xe0ria', u'reuni\xf3 POL']
treeHours = ['06/07/2017 8:17:59', 'Carles', '12/07/2017', '', '9:00 - 10:15, 10:15 - 11:30, 11:30 - 12:45', u'Necess\xe0ria', u'reuni\xf3 amb assessoria'],
class BusyTest(unittest.TestCase):

	def test_gformDataLine_whenBothModesActivated(self):
		line = ['05/07/2017 14:51:14', 'Mate', '11/07/2017', 'Dilluns', '11:30 - 12:45, 12:45 - 14:00', u'Necess\xe0ria', u'reuni\xf3 POL']
		with self.assertRaises(busy.GFormError) as ctx:
			busy.gformDataLine(line)
		self.assertEqual(format(ctx.exception),
				"Indisponibilitat especifica dia puntual 11/07/2017 "
				"i dia de la setmana Dilluns")

	def test_gformDataLine_permanentNotAllowed(self):
		line = ['05/07/2017 14:51:14', 'Mate', '', 'Dilluns', '11:30 - 12:45, 12:45 - 14:00', u'Necess\xe0ria', u'reuni\xf3 POL']
		with self.assertRaises(busy.GFormError) as ctx:
			busy.gformDataLine(line)
		self.assertEqual(format(ctx.exception),
			"Hi ha indisponibilitats permaments al drive, "
			"afegeix-les a ma i esborra-les del drive")

	def test_gformDataLine_singleHour(self):
		line = ['05/07/2017 14:51:14', 'Mate', '11/07/2017', '', '11:30 - 12:45', u'Necess\xe0ria', u'reuni\xf3 POL']
		result = busy.gformDataLine(line)
		self.assertEqual(result,
			('mate', isodate('2017-07-11'), '0010', u'reunió POL'))

	def test_gformDataLine_manyHours(self):
		line = ['05/07/2017 14:51:14', 'Mate', '11/07/2017', '', '9:00 - 10:15, 10:15 - 11:30, 12:45 - 14:00', u'Necess\xe0ria', u'reuni\xf3 POL']
		result = busy.gformDataLine(line)
		self.assertEqual(result,
			('mate', isodate('2017-07-11'), '1101', u'reunió POL'))

	def test_gformDataLine_transliteratesNames(self):
		line = ['05/07/2017 14:51:14', u'María', '11/07/2017', '', '9:00 - 10:15, 10:15 - 11:30, 12:45 - 14:00', u'Necess\xe0ria', u'reuni\xf3 POL']
		result = busy.gformDataLine(line)
		self.assertEqual(result,
			('maria', isodate('2017-07-11'), '1101', u'reunió POL'))


	def test_gform2Singular_firstIgnored(self):
		gform=[
			['headers ignored']*7,
		]
		self.assertEqual(list(busy.gform2Singular(gform)), [
			])

	def test_gform2Singular_singleEntry(self):
		gform=[
			['headers ignored']*7,
			['05/07/2017 14:51:14', u'María', '11/07/2017', '', '9:00 - 10:15, 10:15 - 11:30, 12:45 - 14:00', u'Necess\xe0ria', u'reuni\xf3 POL']
		]
		self.assertEqual(list(busy.gform2Singular(gform)), [
			('maria', isodate('2017-07-11'), '1101', u'reunió POL'),
			])


	def test_singular2Weekly_oneOnMonday(self):
		sequence = busy.singular2Weekly(isodate('2018-01-01'), [
			('maria', isodate('2018-01-01'), '1101', u'reunió POL'),
			])
		self.assertEqual(list(sequence), [
			('maria', u'dl', '1101', u'reuni\xf3 POL'),
		])

	def test_singular2Weekly_oneOnSunday(self):
		sequence = busy.singular2Weekly(isodate('2018-01-01'), [
			('maria', isodate('2018-01-07'), '1101', u'reunió POL'),
			])
		self.assertEqual(list(sequence), [
			('maria', u'dg', '1101', u'reuni\xf3 POL'),
		])

	def test_singular2Weekly_previousIgnored(self):
		sequence = busy.singular2Weekly(isodate('2018-01-01'), [
			('maria', isodate('2017-12-31'), '1101', u'reunió POL'),
			])
		self.assertEqual(list(sequence), [
		])

	def test_singular2Weekly_laterIgnored(self):
		sequence = busy.singular2Weekly(isodate('2018-01-01'), [
			('maria', isodate('2018-01-08'), '1101', u'reunió POL'),
			])
		self.assertEqual(list(sequence), [
		])

	def test_parseBusy_whenEmpty(self):
		lines = [
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			])

	def test_parseBusy_commentsIgnored(self):
		lines = [
			"# comment"
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			])

	def test_parseBusy_emptyLineIgnored(self):
		lines = [
			" "
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			])

	def test_parseBusy_singleDay(self):
		lines = [
			"someone dx 0101 # Reason"
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			ns(
				person='someone',
				weekday='dx',
				turns='0101',
				reason='Reason'
				),
			])

	def test_parseBusy_allDays(self):
		lines = [
			"someone 0101 # Reason"
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			ns(
				person='someone',
				weekday='',
				turns='0101',
				reason='Reason'
				),
			])

	def test_parseBusy_allTurns(self):
		lines = [
			"someone dl # Reason"
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			ns(
				person='someone',
				weekday='dl',
				turns='1111',
				reason='Reason'
				),
			])

	def test_parseBusy_allTurnsAndDays(self):
		lines = [
			"someone  # Reason"
		]
		self.assertEqual(list(busy.parseBusy(lines)), [
			ns(
				person='someone',
				weekday='',
				turns='1111',
				reason='Reason'
				),
			])

	def test_parseBusy_missingReason(self):
		lines = [
			"someone dl 1111"
		]
		with self.assertRaises(Exception) as ctx:
			list(busy.parseBusy(lines))

		self.assertEqual(format(ctx.exception),
			"1: Your have to specify a reason "
			"for the busy event after a # sign")

	def test_parseBusy_emtpyReason(self):
		lines = [
			"someone dl 1111 # "
		]
		with self.assertRaises(Exception) as ctx:
			list(busy.parseBusy(lines))

		self.assertEqual(format(ctx.exception),
			"1: Your have to specify a reason "
			"for the busy event after a # sign")

	def test_parseBusy_shortTurns(self):
		lines = [
			"someone dl 111 # Reason"
		]
		with self.assertRaises(Exception) as ctx:
			list(busy.parseBusy(lines))

		self.assertEqual(format(ctx.exception),
			"1: Expected busy string of lenght 4 "
			"containing '1' on busy hours, found '111'")

	def test_parseBusy_badTurns(self):
		lines = [
			"someone dl 0bad # Reason"
		]
		with self.assertRaises(Exception) as ctx:
			list(busy.parseBusy(lines))

		self.assertEqual(format(ctx.exception),
			"1: Expected busy string of lenght 4 "
			"containing '1' on busy hours, found '0bad'")


	def test_parseBusy_customErrorHandler(self):
		lines = [
			"someone dl 0bad # Reason"
		]
		def handler(msg):
			raise Exception(msg+"Added")

		with self.assertRaises(Exception) as ctx:
			list(busy.parseBusy(lines,handler))

		self.assertEqual(format(ctx.exception),
			"1: Expected busy string of lenght 4 "
			"containing '1' on busy hours, found '0bad'"
			"Added")

	def test_parseBusy_continueAfterErrors(self):
		lines = [
			"someone dl 0bad # Reason",
			"someone dl 111 # Reason",
			"someone dl 1111",
			"someone dl 1111 # ",
			"someone dm 1111 # Reason ",
		]
		errors=[]
		def handler(msg):
			errors.append(msg)

		self.assertEqual(list(busy.parseBusy(lines, handler)), [
			ns(
				person='someone',
				weekday='dm',
				turns='1111',
				reason='Reason'
				),
			])

		self.assertEqual(errors, [
			"1: Expected busy string of lenght 4 "
			"containing '1' on busy hours, found '0bad'",
			"2: Expected busy string of lenght 4 "
			"containing '1' on busy hours, found '111'",
			"3: Your have to specify a reason "
			"for the busy event after a # sign",
			"4: Your have to specify a reason "
			"for the busy event after a # sign",
		])




# vim: noet ts=4 sw=4
