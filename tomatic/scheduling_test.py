#!/usr/bin/env python
# -*- coding: utf8 -*-

from .pbxmockup import weekday
import unittest
from datetime import datetime, timedelta, time
from yamlns.dateutils import Date
from yamlns import namespace as ns
from scheduling import weekstart, nextweek, choosers, Scheduling, solution2schedule

class Scheduling_Test(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def assertNsEqual(self, dict1, dict2):
        def parseIfString(nsOrString):
            if type(nsOrString) in (dict, ns):
                return nsOrString
            return ns.loads(nsOrString)

        def sorteddict(d):
            if type(d) not in (dict, ns):
                return d
            return ns(sorted(
                (k, sorteddict(v))
                for k,v in d.items()
                ))
        dict1 = sorteddict(parseIfString(dict1))
        dict2 = sorteddict(parseIfString(dict2))

        return self.assertMultiLineEqual(dict1.dump(), dict2.dump())



    # weekday

    def test_weekday_withSunday(self):
        self.assertEqual(
            'dg', weekday(Date("2017-10-01")))

    def test_weekday_withMonday(self):
        self.assertEqual(
            'dl', weekday(Date("2017-10-02")))

    def test_weekday_withWenesday(self):
        self.assertEqual(
            'dx', weekday(Date("2017-10-04")))

    # weekstart

    def test_weekstart_withMonday(self):
        self.assertEqual(
            weekstart(Date("2017-10-02")),
            Date("2017-10-02"))

    def test_weekstart_withFriday(self):
        self.assertEqual(
            weekstart(Date("2017-10-06")),
            Date("2017-10-02"))

    # nextweek

    def test_nextweek_withMonday(self):
        self.assertEqual(
            nextweek(Date("2017-10-02")),
            Date("2017-10-09"))

    def test_nextweek_withFriday(self):
        self.assertEqual(
            nextweek(Date("2017-10-06")),
            Date("2017-10-09"))

    # extension

    def test_extension_existing(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extension('cesar'),
            '200')

    def test_extension_badExtension(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extension('notExisting'),
            None)

    # extensionToName

    def test_extensionToName_stringExtension(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extensionToName('200'),
            'cesar')

    def test_extensionToName_intExtension(self):
        schedule = Scheduling("""\
            extensions:
              cesar: 200
            """)
        self.assertEqual(
            schedule.extensionToName(200),
            'cesar')

    # properName

    def test_properName_whenPresent(self):
        schedule = Scheduling("""\
            names:
              cesar: César
            """)
        self.assertEqual(
            schedule.properName('cesar'),
            u'César')

    def test_properName_missing_usesTitle(self):
        schedule = Scheduling("""\
            names:
              cesar: César
            """)
        self.assertEqual(
            schedule.properName('perico'),
            u'Perico')

    def test_properName_noNamesAtAll(self):
        schedule = Scheduling("""\
            otherkey:
            """)
        self.assertEqual(
            schedule.properName('perico'),
            u'Perico')

    # intervals

    def test_intervals_withOneDate_notEnough(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            """)
        self.assertEqual(
            schedule.intervals(), [
            ])

    def test_intervals_withTwoDates(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            """)
        self.assertEqual(
            schedule.intervals(), [
            '09:00-10:15',
            ])

    def test_intervals_withMoreThanTwo(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.intervals(), [
            '09:00-10:15',
            '10:15-11:30',
            ])

    # peekInterval

    def test_peekInterval_beforeAnyInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("08:59"),None)

    def test_peekInterval_justInFirstInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("09:00"),0)

    def test_peekInterval_justBeforeNextInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("10:14"),0)

    def test_peekInterval_justInNextInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("10:15"),1)

    def test_peekInterval_justAtTheEndOfLastInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("11:29"),1)

    def test_peekInterval_pastLastInterval(self):
        schedule = Scheduling("""\
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            """)
        self.assertEqual(
            schedule.peekInterval("11:30"),None)

    def test_peekInterval_withNoHours(self):
        schedule = Scheduling("""\
            other:
            """)
        with self.assertRaises(Exception) as ctx:
            schedule.peekInterval("11:30")
        self.assertEqual(str(ctx.exception),
            "Schedule with no hours attribute")

    # choosers

    def test_choosers(self):
        now = datetime(2017,10,20,15,25,35)
        self.assertEqual(
            choosers(now),
            ("2017-10-16", 'dv', "15:25"))

    # peekQueue

    def test_peekQueue_oneSlot_oneTurn(self):
        schedule = Scheduling(u"""\
            timetable:
              dl:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'cesar',
            ])

    def test_peekQueue_oneSlot_twoTurns(self):
        schedule = Scheduling(u"""\
            timetable:
              'dl':
              -
                - cesar
                - eduard
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'cesar',
            'eduard',
            ])

    def test_peekQueue_twoTimes(self):
        schedule = Scheduling(u"""\
            timetable:
              dl:
              -
                - cesar
              -
                - eduard
            hours:
            - '00:00'
            - '12:00'
            - '23:59'

            extensions:
              cesar: 200
              eduard: 201
            """)
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'eduard',
            ])

    def test_peekQueue_beforeTime(self):
        schedule = Scheduling(u"""\
            timetable:
              dl:
              -
                - cesar
            hours:
            - '23:58'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dl', '12:00'), [
            ])

    def test_peekQueue_afterTime(self):
        schedule = Scheduling(u"""\
            timetable:
              dl:
              -
                - cesar
            hours:
            - '00:00'
            - '00:01'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            ])

    def test_peekQueue_holiday(self):
        schedule = Scheduling(u"""\
            timetable:
              dm:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            ])

    def test_peekQueue_aDifferentDay(self):
        schedule = Scheduling(u"""\
            timetable:
              dm:
              -
                - cesar
            hours:
            - '00:00'
            - '23:59'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dm','12:00'), [
            'cesar',
            ])

    def test_peekQueue_dictFormat(self):
        schedule = Scheduling(u"""\
            timetable:
              dl:
                1:
                - cesar
            hours:
            - '00:00'
            - '24:00'

            extensions:
              cesar: 200
            """)
        self.assertEqual(schedule.peekQueue('dl','12:00'), [
            'cesar',
            ])

    @unittest.skip("TODO")
    def test_peekQueue_withNobodySlots(self): pass

    # solution2schedule

    def config_singleSlot(self):
        return ns.loads("""\
            nTelefons: 1
            diesVisualitzacio: ['dl']
            hours:  # La darrera es per tancar
            - '09:00'
            - '10:15'
            colors:
                ana: aa11aa
                belen: bb22bb
            extensions:
                ana: 1001
                belen: 1002
            names: {}
        """)

    def config_twoLines(self):
        c = self.config_singleSlot()
        c.nTelefons = 2
        return c

    def config_twoDays(self):
        c = self.config_singleSlot()
        c.diesVisualitzacio.append('dm')
        return c

    def config_twoTimes(self):
        c = self.config_singleSlot()
        c.hours.append('11:30')
        return c

    def config_twoEverything(self):
        c = self.config_singleSlot()
        c.diesVisualitzacio.append('dm')
        c.hours.append('11:30')
        c.nTelefons = 2
        return c


    def test_solution2schedule_oneholiday(self):
        config = self.config_singleSlot()

        result=solution2schedule(
            date=datetime.strptime(
                '2016-07-11','%Y-%m-%d').date(),
            config=config,
            solution={},
        )
        self.assertNsEqual(result, """\
            week: '2016-07-11'
            days:
            - dl
            hours:
            - '09:00'
            - '10:15'
            turns:
            - 'T1'
            timetable:
              dl:
              - - festiu
            colors:
              ana:   aa11aa
              belen: bb22bb
            extensions:
              ana:   1001
              belen: 1002
            names: {}
            """)

    def test_solution2schedule_noWeekNextMonday(self):
        config = self.config_singleSlot()

        result=solution2schedule(
            # no date specified
            config=config,
            solution={},
        )

        today = Date.today()
        week=datetime.strptime(result.week, "%Y-%m-%d").date()
        self.assertEqual(week.weekday(),0) # Monday
        self.assertTrue(week > today) # in the future
        self.assertTrue(week <= today+timedelta(days=7)) # A week at most

    def test_solution2schedule_oneslot(self):
        config = self.config_singleSlot()

        result=solution2schedule(
            date=datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            config=config,
            solution={
                ('dl',0,0):'ana',
            },
        )

        self.assertNsEqual( result, """
            week: '2016-07-18'
            days:
            - dl
            hours:
            - '09:00'
            - '10:15'
            turns:
            - 'T1'
            timetable:
              dl:
              - - ana
            colors:
              ana:   aa11aa
              belen: bb22bb
            extensions:
              ana:   1001
              belen: 1002
            names: {}
        """)

    def test_solution2schedule_manyLines(self):
        config = self.config_twoLines()

        result=solution2schedule(
            date=datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            config=config,
            solution={
                ('dl',0,0):'ana',
                ('dl',0,1):'belen',
            },
        )

        self.assertNsEqual( result, """
            week: '2016-07-18'
            days:
            - dl
            hours:
            - '09:00'
            - '10:15'
            turns:
            - 'T1'
            - 'T2'
            timetable:
              dl:
              - - ana
                - belen
            colors:
              ana: 'aa11aa'
              belen: 'bb22bb'
            extensions:
              ana:   1001
              belen: 1002
            names: {}
        """)

    def test_solution2schedule_manyTimes(self):
        config = self.config_twoTimes()

        result=solution2schedule(
            date=datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            config=config,
            solution={
                ('dl',0,0):'ana',
                ('dl',1,0):'belen',
            },
        )

        self.assertNsEqual( result, """
            week: '2016-07-18'
            days:
            - dl
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            turns:
            - 'T1'
            timetable:
              dl:
              - - ana
              - - belen
            colors:
              ana: 'aa11aa'
              belen: 'bb22bb'
            extensions:
              ana:   1001
              belen: 1002
            names: {}
        """)

    def test_solution2schedule_manyDays(self):
        config = self.config_twoDays()

        result=solution2schedule(
            date=datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            config=config,
            solution={
                ('dl',0,0):'ana',
                ('dm',0,0):'belen',
            },
        )

        self.assertNsEqual(result, """
            week: '2016-07-18'
            days:
            - dl
            - dm
            hours:
            - '09:00'
            - '10:15'
            turns:
            - 'T1'
            timetable:
              dl:
              - - ana
              dm:
              - - belen
            colors:
              ana:   'aa11aa'
              belen: 'bb22bb'
            extensions:
              ana:   1001
              belen: 1002
            names: {}
        """)

    def test_solution2schedule_manyEverything(self):
        config = self.config_twoEverything()

        result=solution2schedule(
            date=datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            config=config,
            solution={
                ('dl',0,0):'ana',
                ('dl',1,0):'belen',
                ('dm',0,1):'carla',
                ('dm',1,1):'diana',
            },
        )

        self.assertNsEqual(result, """
            week: '2016-07-18'
            days:
            - dl
            - dm
            hours:
            - '09:00'
            - '10:15'
            - '11:30'
            turns:
            - 'T1'
            - 'T2'
            timetable:
              dl:
              - - ana
                - festiu
              - - belen
                - festiu
              dm:
              - - festiu
                - carla
              - - festiu
                - diana
            colors:
              ana:   'aa11aa'
              belen: 'bb22bb'
            extensions:
              ana:   1001
              belen: 1002
            names: {}
        """)

    completeConfig="""\
        nTelefons: 3
        diesCerca: ['dx','dm','dj', 'dl', 'dv',] # Els mes conflictius davant
        diesVisualitzacio: ['dl','dm','dx','dj','dv']

        hours:  # La darrera es per tancar
        - '09:00'
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        randomColors: false # Si vols generar colors aleatoris o fer cas de 'colors'
        colors:
            marc:   'fbe8bc'
            eduard: 'd8b9c5'
            pere:   '8f928e'
            david:  'ffd3ac'
            aleix:  'eed0eb'
            carles: 'c98e98'
            marta:  'eb9481'
            monica: '7fada0'
            yaiza:  '90cdb9'
            erola:  '8789c8'
            manel:  '88dfe3'
            tania:  'c8abf4'
            judit:  'e781e8'
            silvia: '8097fa'
            joan:   'fae080'
            ana:    'aa11aa'
            victor: 'ff3333'
            jordi:  'ff9999'
            cesar:  '889988'
        extensions:
            marta:  3040
            monica: 3041
            manel:  3042
            erola:  3043
            yaiza:  3044
            eduard: 3045
            marc:   3046
            judit:  3047
            judith: 3057
            tania:  3048
            carles: 3051
            pere:   3052
            aleix:  3053
            david:  3054
            silvia: 3055
            joan:   3056
            ana:    1001
            victor: 3182
            jordi:  3183
        names: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
       """

    def test_solution2schedule_completeTimetable(self):
        result=solution2schedule(
            config=ns.loads(self.completeConfig),
            solution={
                ('dl',0,0):'jordi',
                ('dl',0,1):'marta',
                ('dl',0,2):'tania',
                ('dl',1,0):'tania',
                ('dl',1,1):'yaiza',
                ('dl',1,2):'silvia',
                ('dl',2,0):'judith',
                ('dl',2,1):'pere',
                ('dl',2,2):'ana',
                ('dl',3,0):'ana',
                ('dl',3,1):'judith',
                ('dl',3,2):'erola',
                ('dm',0,0):'pere',
                ('dm',0,1):'jordi',
                ('dm',0,2):'victor',
                ('dm',1,0):'carles',
                ('dm',1,1):'victor',
                ('dm',1,2):'ana',
                ('dm',2,0):'joan',
                ('dm',2,1):'silvia',
                ('dm',2,2):'eduard',
                ('dm',3,0):'david',
                ('dm',3,1):'joan',
                ('dm',3,2):'monica',
                ('dx',0,0):'yaiza',
                ('dx',0,1):'monica',
                ('dx',0,2):'pere',
                ('dx',1,0):'erola',
                ('dx',1,1):'joan',
                ('dx',1,2):'marta',
                ('dx',2,0):'victor',
                ('dx',2,1):'eduard',
                ('dx',2,2):'jordi',
                ('dx',3,0):'eduard',
                ('dx',3,1):'david',
                ('dx',3,2):'victor',
                ('dj',0,0):'judith',
                ('dj',0,1):'jordi',
                ('dj',0,2):'carles',
                ('dj',1,0):'silvia',
                ('dj',1,1):'tania',
                ('dj',1,2):'judith',
                ('dj',2,0):'monica',
                ('dj',2,1):'ana',
                ('dj',2,2):'judit',
                ('dj',3,0):'judit',
                ('dj',3,1):'erola',
                ('dj',3,2):'joan',
                ('dv',0,0):'ana',
                ('dv',0,1):'judith',
                ('dv',0,2):'jordi',
                ('dv',1,0):'jordi',
                ('dv',1,1):'ana',
                ('dv',1,2):'judith',
                ('dv',2,0):'victor',
                ('dv',2,1):'carles',
                ('dv',2,2):'yaiza',
                ('dv',3,0):'marta',
                ('dv',3,1):'victor',
                ('dv',3,2):'silvia',
                },
            date=datetime.strptime(
                '2016-07-11','%Y-%m-%d').date(),
        )

        self.assertNsEqual(result, """\
                week: '2016-07-11'
                days:
                - dl
                - dm
                - dx
                - dj
                - dv
                hours:
                - '09:00'
                - '10:15'
                - '11:30'
                - '12:45'
                - '14:00'
                turns:
                - T1
                - T2
                - T3
                timetable:
                  dl:
                  - - jordi
                    - marta
                    - tania
                  - - tania
                    - yaiza
                    - silvia
                  - - judith
                    - pere
                    - ana
                  - - ana
                    - judith
                    - erola
                  dm:
                  - - pere
                    - jordi
                    - victor
                  - - carles
                    - victor
                    - ana
                  - - joan
                    - silvia
                    - eduard
                  - - david
                    - joan
                    - monica
                  dx:
                  - - yaiza
                    - monica
                    - pere
                  - - erola
                    - joan
                    - marta
                  - - victor
                    - eduard
                    - jordi
                  - - eduard
                    - david
                    - victor
                  dj:
                  - - judith
                    - jordi
                    - carles
                  - - silvia
                    - tania
                    - judith
                  - - monica
                    - ana
                    - judit
                  - - judit
                    - erola
                    - joan
                  dv:
                  - - ana
                    - judith
                    - jordi
                  - - jordi
                    - ana
                    - judith
                  - - victor
                    - carles
                    - yaiza
                  - - marta
                    - victor
                    - silvia
                colors:
                  marc:   'fbe8bc'
                  eduard: 'd8b9c5'
                  pere:   '8f928e'
                  david:  'ffd3ac'
                  aleix:  'eed0eb'
                  carles: 'c98e98'
                  marta:  'eb9481'
                  monica: '7fada0'
                  yaiza:  '90cdb9'
                  erola:  '8789c8'
                  manel:  '88dfe3'
                  tania:  'c8abf4'
                  judit:  'e781e8'
                  silvia: '8097fa'
                  joan:   'fae080'
                  ana:    'aa11aa'
                  victor: 'ff3333'
                  jordi:  'ff9999'
                  cesar:  '889988'
                extensions:
                  marta:  3040
                  monica: 3041
                  manel:  3042
                  erola:  3043
                  yaiza:  3044
                  eduard: 3045
                  marc:   3046
                  judit:  3047
                  judith: 3057
                  tania:  3048
                  carles: 3051
                  pere:   3052
                  aleix:  3053
                  david:  3054
                  silvia: 3055
                  joan:   3056
                  ana:    1001
                  victor: 3182
                  jordi:  3183
                names:
                  silvia: Sílvia
                  monica: Mònica
                  tania:  Tània
                  cesar:  César
                  victor: Víctor
            """)


unittest.TestCase.__str__ = unittest.TestCase.id

# vim: ts=4 sw=4 et
