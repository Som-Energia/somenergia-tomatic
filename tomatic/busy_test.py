#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
from . import busy
from .busy import isodate
from yamlns import namespace as ns

def open(*args, **kwd):
	import io
	return io.open(encoding='utf8', *args, **kwd)

dl='Dilluns'
date='11/07/2017'
ts='05/07/2017 14:51:14'
user='Mate'
t9='9:00 - 10:15'
t10='10:15 - 11:30'
t11='11:30 - 12:45'
t12='12:45 - 14:00'
def turns(*ts):
	return ', '.join(ts)
needed=u'Necessària'
optional=u'Descartable'
reason=u'reunió POL'

class BusyTest(unittest.TestCase):

	def setUp(self):
		self.maxDiff=None
		self.todelete=[]

	def tearDown(self):
		for filename in self.todelete:
			os.remove(filename)

	def write(self, filename, content):
		with open(filename,'w') as f:
			f.write(content)
		self.todelete.append(filename)

	def assertContentEqual(self, filename, content):
		with open(filename) as f:
			actual = f.read()
		self.assertMultiLineEqual(content, actual)

	def test_gformDataLine_whenBothModesActivated(self):
		line = [ts, user, date, dl, turns(t11,t12), needed, reason]
		with self.assertRaises(busy.GFormError) as ctx:
			busy.gformDataLine(line)
		self.assertEqual(format(ctx.exception),
				"Indisponibilitat especifica dia puntual 11/07/2017 "
				"i dia de la setmana Dilluns")

	def test_gformDataLine_permanentNotAllowed(self):
		line = [ts, user, '', dl, turns(t11,t12), needed, reason]
		with self.assertRaises(busy.GFormError) as ctx:
			busy.gformDataLine(line)
		self.assertEqual(format(ctx.exception),
			"Hi ha indisponibilitats permaments al drive, "
			"afegeix-les a ma i esborra-les del drive")

	def tupleToNs(self, opcional, person, when, turns, reason):
		import datetime
		if type(when) == datetime.date:
			when = dict(date=when)
		else:
			when = dict(weekday=when)
		return ns(
			optional = opcional!='F',
			person = person,
			turns = turns,
			reason = reason,
			**when)

	from somutils.testutils import assertNsEqual
	def assertBusyEqual(self, result, expected):
		self.assertNsEqual(result, self.tupleToNs(*expected))

	def assertBusyListEqual(self, result, expected):
		result = ns(lines=[
			entry
			for entry in result
			])
		expected = ns(lines=[
			self.tupleToNs(*entry)
			for entry in expected
			])

		self.assertNsEqual(result, expected)

	def test_gformDataLine_singleHour(self):
		line = [ts, user, date, '', t11, needed, reason]
		result = busy.gformDataLine(line)
		self.assertBusyEqual(result,
			('F', 'mate', isodate('2017-07-11'), '0010', u'reunió POL'))

	def test_gformDataLine_manyHours(self):
		line = [ts, user, date, '', turns(t9,t10,t12), needed, reason]
		result = busy.gformDataLine(line)
		self.assertBusyEqual(result,
			('F', 'mate', isodate('2017-07-11'), '1101', u'reunió POL'))

	def test_gformDataLine_transliteratesNames(self):
		line = [ts, u'María', date, '', turns(t9,t10,t11,t12), needed, reason]
		result = busy.gformDataLine(line)
		self.assertBusyEqual(result,
			('F', 'maria', isodate('2017-07-11'), '1111', u'reunió POL'))

	def test_gformDataLine_withOptional(self):
		line = [ts, 'Mate', date, '', turns(t9,t10,t11,t12), optional, reason]
		result = busy.gformDataLine(line)
		self.assertBusyEqual(result,
			('O', 'mate', isodate('2017-07-11'), '1111', u'reunió POL'))


	def test_gform2Singular_firstIgnored(self):
		gform=[
			['headers ignored']*7,
		]
		self.assertEqual(list(busy.gform2Singular(gform)), [
			])

	def test_gform2Singular_singleEntry(self):
		gform=[
			['headers ignored']*7,
			[ts, u'María', date, '', turns(t9,t10,t12), needed, u'reuni\xf3 POL']
		]
		self.assertBusyListEqual(list(busy.gform2Singular(gform)), [
			('F', 'maria', isodate('2017-07-11'), '1101', u'reunió POL'),
			])


	def test_onWeek_oneOnMonday(self):
		sequence = busy.onWeek(isodate('2018-01-01'), [
			self.tupleToNs('F', 'maria', isodate('2018-01-01'), '1101', u'reunió POL'),
			])
		self.assertBusyListEqual(list(sequence), [
			('F', 'maria', u'dl', '1101', u'reuni\xf3 POL'),
		])

	def test_onWeek_oneOnFriday(self):
		sequence = busy.onWeek(isodate('2018-01-01'), [
			self.tupleToNs('F','maria', isodate('2018-01-05'), '1101', u'reunió POL'),
			])
		self.assertBusyListEqual(list(sequence), [
			('F','maria', u'dv', '1101', u'reuni\xf3 POL'),
		])

	def test_onWeek_optional(self):
		sequence = busy.onWeek(isodate('2018-01-01'), [
			self.tupleToNs('O', 'maria', isodate('2018-01-01'), '1101', u'reunió POL'),
			])
		self.assertBusyListEqual(list(sequence), [
			('O', 'maria', u'dl', '1101', u'reuni\xf3 POL'),
		])

	def test_onWeek_earlyDateIgnored(self):
		sequence = busy.onWeek(isodate('2018-01-01'), [
			self.tupleToNs('F','maria', isodate('2017-12-31'), '1101', u'reunió POL'),
			])
		self.assertBusyListEqual(list(sequence), [
		])

	def test_onWeek_lateDateIgnored(self):
		sequence = busy.onWeek(isodate('2018-01-01'), [
			self.tupleToNs('F','maria', isodate('2018-01-06'), '1101', u'reunió POL'),
			])
		self.assertBusyListEqual(list(sequence), [
		])

	def test_onWeek_weekdayPasses(self):
		sequence = busy.onWeek(isodate('2018-01-01'), [
			self.tupleToNs('F','maria', 'dl', '1101', u'reunió POL'),
			])
		self.assertBusyListEqual(list(sequence), [
			('F', 'maria', u'dl', '1101', u'reunió POL'),
			])

	def assertParsed(self, result, expected):
		self.assertNsEqual(ns(data=list(result)), ns(data=expected))

	def test_parseBusy_whenEmpty(self):
		lines = [
		]
		self.assertParsed(busy.parseBusy(lines), [
			])

	def test_parseBusy_commentsIgnored(self):
		lines = [
			"# comment"
		]
		self.assertParsed(busy.parseBusy(lines), [
			])

	def test_parseBusy_emptyLineIgnored(self):
		lines = [
			" "
		]
		self.assertParsed(busy.parseBusy(lines), [
			])

	def test_parseBusy_singleWeekDay(self):
		lines = [
			"someone dx 0101 # Reason"
		]
		self.assertParsed(busy.parseBusy(lines), [
			ns(
				person='someone',
				weekday='dx',
				turns='0101',
				reason='Reason',
				optional=True,
				),
			])

	def test_parseBusy_forced(self):
		lines = [
			"+someone dx 0101 # Reason" # a plus behind
		]
		self.assertParsed(busy.parseBusy(lines), [
			ns(
				person='someone',
				weekday='dx',
				turns='0101',
				reason='Reason',
				optional=False,
				),
			])

	def test_parseBusy_allWeek(self):
		lines = [
			"someone 0101 # Reason"
		]
		self.assertParsed(busy.parseBusy(lines), [
			ns(
				person='someone',
				weekday='',
				turns='0101',
				reason='Reason',
				optional=True,
				),
			])

	def test_parseBusy_singleDay(self):
		lines = [
			"someone 2015-01-02 0101 # Reason"
		]
		self.assertParsed(busy.parseBusy(lines), [
			ns(
				person='someone',
				date=isodate('2015-01-02'),
				turns='0101',
				reason='Reason',
				optional=True,
				),
			])

	def test_parseBusy_allTurns(self):
		lines = [
			"someone dl # Reason"
		]
		self.assertParsed(busy.parseBusy(lines), [
			ns(
				person='someone',
				weekday='dl',
				turns='1111',
				reason='Reason',
				optional=True,
				),
			])

	def test_parseBusy_allTurnsAndDays(self):
		lines = [
			"someone  # Reason"
		]
		self.assertParsed(busy.parseBusy(lines), [
			ns(
				person='someone',
				weekday='',
				turns='1111',
				reason='Reason',
				optional=True,
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

	def test_parseBusy_spacesConsideredEmpty(self):
		lines = [
			"  # Reason",
		]
		errors=[]
		def handler(msg):
			errors.append(msg)

		self.assertBusyListEqual(list(busy.parseBusy(lines, handler)), [
		])
		self.assertEqual(errors, [])

	def test_parseBusy_continueAfterErrors(self):
		lines = [
			"someone dl 0bad # Reason",
			"someone dm 111 # Reason",
			"someone dx 1011",
			"someone dj 1101 # ",
			"someone dv 1110 # Reason ",
		]
		errors=[]
		def handler(msg):
			errors.append(msg)

		self.assertParsed(busy.parseBusy(lines, handler), [
			ns(
				person='someone',
				weekday='dx',
				turns='1011',
				reason='',
				optional=True,
				),
			ns(
				person='someone',
				weekday='dj',
				turns='1101',
				reason='',
				optional=True,
				),
			ns(
				person='someone',
				weekday='dv',
				turns='1110',
				reason='Reason',
				optional=True,
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

	def test_formatItem_withWeekday(self):
		item = ns(
			person='someone',
			weekday='dm',
			turns='1111',
			reason=u'La razón',
			optional=True,
			)
		self.assertEqual(
			busy.formatItem(item),
			"someone dm 1111 # La razón\n"
			)

	def test_formatItem_withDate(self):
		item = ns(
			person='someone',
			date=isodate('2015-02-03'),
			turns='1111',
			reason=u'La razón',
			optional=True,
			)
		self.assertEqual(
			busy.formatItem(item),
			"someone 2015-02-03 1111 # La razón\n"
			)

	def test_formatItem_forced(self):
		item = ns(
			person='someone',
			weekday='dm',
			turns='1111',
			reason=u'La razón',
			optional=False,
			)
		self.assertEqual(
			busy.formatItem(item),
			"+someone dm 1111 # La razón\n"
			)

	def test_updatePerson_noPreviousEntries(self):
		self.write('testfile', '')
		result = busy.updatePerson('testfile','someone', [
			ns(
				weekday='dl',
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			])
				
		self.assertMultiLineEqual(result,
			"+someone dl 1111 # La razón\n"
			)

	def test_updatePerson_appendMany(self):
		self.write('testfile','')

		result = busy.updatePerson('testfile','someone', [
			ns(
				weekday='dl',
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			ns(
				weekday='dm',
				turns='0001',
				reason=u'Otra razón',
				optional=True,
				),
			])
				
		self.assertMultiLineEqual(result,
			"+someone dl 1111 # La razón\n"
			"someone dm 0001 # Otra razón\n"
			)

	def test_updatePerson_keepsOtherPeopleEntries(self):
		self.write('testfile',
			"someother dx 1000 # Another reason\n"
			)

		result = busy.updatePerson('testfile','someone', [
			ns(
				weekday='dl',
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			])

		self.assertMultiLineEqual(result,
			"someother dx 1000 # Another reason\n"
			"+someone dl 1111 # La razón\n"
			)

	def test_updatePerson_removeExistingOfSamePerson(self):
		self.write('testfile',
			"+someone dm 0100 # A reason\n"
			"someother dx 1000 # Another reason\n"
			)

		result = busy.updatePerson('testfile','someone', [
			ns(
				weekday='dl',
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			])
				
		self.assertMultiLineEqual(result,
			"someother dx 1000 # Another reason\n"
			"+someone dl 1111 # La razón\n"
			)

	def test_updatePerson_emptyUpdateClears(self):
		self.write('testfile',
			"+someone dm 0100 # A reason\n"
			"someother dx 1000 # Another reason\n"
			)

		result = busy.updatePerson('testfile','someone', [
			])

		self.assertMultiLineEqual(result,
			"someother dx 1000 # Another reason\n"
			)

	def test_updatePerson_badOriginal(self):
		self.write('testfile',
			"badfile caca # comment\n"
			)

		with self.assertRaises(Exception) as ctx:
			busy.updatePerson('testfile','someone', [
				])
		self.assertEqual(format(ctx.exception),
			"1: Expected busy string of lenght 4 containing '1' on busy hours, found 'caca'")

	def test_updatePerson_badOriginal_customHandler(self):
		self.write('testfile',
			"badfile caca # comment\n"
			)
		errors=[]
		def handler(error):
			errors.append(error)
			raise Exception(error)

		with self.assertRaises(Exception) as ctx:
			busy.updatePerson('testfile','someone', [
				], handler)
		self.assertEqual(format(ctx.exception),
			"1: Expected busy string of lenght 4 containing '1' on busy hours, found 'caca'")
		self.assertEqual(errors, [
			"1: Expected busy string of lenght 4 containing '1' on busy hours, found 'caca'",
			])

	def test_updatePerson_badNewEntries(self):
		self.write('testfile',
			"someone dl 0001 # comment\n"
			"somebody dm 1001 # comment\n"
			)

		with self.assertRaises(AttributeError) as ctx: # TODO: Custom exception
			busy.updatePerson('testfile','someone', [
				ns() # bad
				])
		self.assertEqual(format(ctx.exception),
			'optional')

	def test_justPerson_whenNoEntries(self):
		result = busy.justPerson('someone', [
			])
		self.assertNsEqual(ns(d=result),
			"d: []\n"
			)

	def test_justPerson_removesPersonField(self):
		result = busy.justPerson('someone', [
			ns(
				person='someone',
				weekday='dl',
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			])
		self.assertNsEqual(ns(d=result),
			"d:\n"
			"- weekday: dl\n"
			"  turns: '1111'\n"
			"  reason: La razón\n"
			"  optional: false\n"
			)

	def test_justPerson_otherPersons(self):
		result = busy.justPerson('someone', [
			ns(
				person='other',
				weekday='dl',
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			])
		self.assertNsEqual(ns(d=result),
			"d: []\n"
			)

	def test_justPerson_many(self):
		result = busy.justPerson('someone', [
			ns(
				person='someone',
				weekday='dl',
				turns='1000',
				reason=u'La razón 1',
				optional=False,
				),
			ns(
				person='other',
				weekday='dx',
				turns='0100',
				reason=u'La razón 2',
				optional=False,
				),
			ns(
				person='someone',
				weekday='dm',
				turns='0010',
				reason=u'La razón 3',
				optional=True,
				),
			])
		self.assertNsEqual(ns(d=result),
			"d:\n"
			"- weekday: dl\n"
			"  turns: '1000'\n"
			"  reason: La razón 1\n"
			"  optional: false\n"
			"- weekday: dm\n"
			"  turns: '0010'\n"
			"  reason: La razón 3\n"
			"  optional: true\n"
			)


	def test_justPerson_returnsStringDate(self):
		result = busy.justPerson('someone', [
			ns(
				person='someone',
				date=isodate('2015-01-23'),
				turns='1111',
				reason=u'La razón',
				optional=False,
				),
			])
		self.assertNsEqual(ns(d=result),
			"d:\n"
			"- date: '2015-01-23'\n"
			"  turns: '1111'\n"
			"  reason: La razón\n"
			"  optional: false\n"
			)


	def test_checkEntry_whenOk(self):
		busy.checkEntry('weekly', ns(
			weekday='dl',
			reason="A reason",
			turns='1000',
			optional=True,
			))

	def test_checkEntry_missingWeekday(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				reason="A reason",
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Missing field 'weekday'")

	def test_checkEntry_missingReason(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Missing field 'reason'")

	def test_checkEntry_missingTurns(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				reason="A reason",
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Missing field 'turns'")

	def test_checkEntry_missingOptional(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				reason="A reason",
				turns='1000',
				))
		self.assertEqual(format(ctx.exception),
			"Missing field 'optional'")

	def test_checkEntry_badWeekday(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='bad', # changed
				reason="A reason",
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Bad weekday 'bad', should be dl, dm, dx, dj, dv or empty")

	def test_checkEntry_badOptional(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				reason="A reason",
				turns='1000',
				optional=None, # changed
				))
		self.assertEqual(format(ctx.exception),
			"Bad value for 'optional'. Expected a boolean but was 'None'")

	def test_checkEntry_badReasonType(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				reason=None, # changed
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Invalid type 'NoneType' for field 'reason'")

	def test_checkEntry_emptyReason(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				reason='  ', # changed
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"No heu indicat el motiu de la indisponibilitat")

	def test_checkEntry_badTurns(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				weekday='dl',
				reason='A reason',
				turns='bad', # changed
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Attribute 'turns' should be a text with 4 ones or zeroes, but was 'bad'")

	def test_checkEntry_unexpectedField(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('weekly', ns(
				date='2015-02-12', # added
				weekday='dl',
				reason='A reason',
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Unexpected field 'date'")

	def test_checkEntry_oneshot_withWeekday(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('oneshot', ns(
				weekday='dl', # added
				reason='A reason',
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Unexpected field 'weekday'")

	def test_checkEntry_oneShot_baddate(self):
		with self.assertRaises(Exception) as ctx:
			busy.checkEntry('oneshot', ns(
				date='bad', # added
				reason='A reason',
				turns='1000',
				optional=True,
				))
		self.assertEqual(format(ctx.exception),
			"Field 'date' should be a date but was 'bad'")
			#"Field 'date' should be a date in ISO format YYYY-MM-DD")

	def test_checkEntry_oneShot(self):
		busy.checkEntry('oneshot', ns(
			date='2015-02-12', # added
			reason='A reason',
			turns='1000',
			optional=True,
			))


	def test_weekdays(self):
		holidays= [
			# Inventados
			('2020-11-25', 'Nadal'),
			('2020-11-26', 'Sant Esteve'),
		]
		self.assertEqual(
			busy.laborableWeekDays(isodate('2020-11-23'), holidays),
			['dl', 'dm', 'dv'])

	def test_weekdays_defaultlist(self):
		self.assertEqual(
			busy.laborableWeekDays(isodate('2020-12-21')),
			['dl', 'dm', 'dx'])

	def test_weekdays_notAMonday(self):
		self.assertEqual(
			busy.laborableWeekDays(isodate('2020-12-25')),
			['dl', 'dm', 'dx'])




# vim: noet ts=4 sw=4
