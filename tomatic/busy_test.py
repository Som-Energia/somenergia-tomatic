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




	# TODO: accents


# vim: noet ts=4 sw=4
