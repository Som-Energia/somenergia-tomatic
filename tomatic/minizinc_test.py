# -*- encoding: utf-8 -*-
import unittest
import datetime
from unittest.mock import patch

from yamlns import namespace as ns

from .minizinc import Minizinc
from .busy import weekdays as fullWeekdays
from pathlib import Path


def fixture(**overrides):
    result = ns(ns(
        monday=datetime.date(2023, 3, 27),
        deterministic=True,
        minizincSolvers=['chuffed', 'coin-bc'],
        finalLoad=ns(
            goku=4,
            vegeta=4,
            krilin=4,
        ),
        maximHoresDiariesGeneral=2,
        nTelefons=2,
        hours=['8:00', '9:00'],
        busyFiles=['indisponibilitats.conf'],
        overloadfile='overload.yaml',
        names=[],
        colors=[],
        extensions=[],
    ), **overrides)
    return result


from somutils.testutils import sandbox_dir

class Minizinc_Test(unittest.TestCase):
    from somutils.testutils import assertNsEqual
    from somutils.testutils import enterContext

    def setUp(self):
        self.sandbox = self.enterContext(sandbox_dir())
        self.holidaysfile = Path('holidays.conf')
        self.holidaysfile.write_text(
            "2020-12-24\tNadal\n"
            "2020-12-25\tNadal\n"
            "2020-12-26\tNadal\n"
            "2023-09-12\tFake holiday\n"
            "",
            encoding='utf8',
        )
        self.overload = Path('overload.yaml')
        self.overload.write_text("{}")
        Path('indisponibilitats.conf').write_text(
            '+goku dl 1000 # Fight Freezer\n'
            '+goku dv 1000 # Train\n'
            '+vegeta dm 1000 # Date with Bulma\n'
            '+krilin dx 1000 # Explode\n'
            '+krilin dj 1000 # Resurect\n'
            'goku dj 1000 # Sleepy\n'
            'krilin dm 1000 # Eating\n'
            'arale dj 1000 # Ignored Dr Slump\n'
            'goku dj 0100 # Ignored hour\n'
        )

    def test_create_menu_instance(self):
        # Given a config with all the needed paramenters
        # when we initialize a Minizinc
        config = fixture()
        minizinc = Minizinc(config)
        # then we have an instance of Minizinc
        self.assertIsInstance(minizinc, Minizinc)

    def test_shuffle_persons(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        config = fixture()
        minizinc = Minizinc(config)
        given_persons = list(config.finalLoad.keys())
        shuffled_persons = minizinc.problem.names
        # then we have the persons shuffled with ningu added
        self.assertEqual(
            set(shuffled_persons),
            set(given_persons).union({'ningu'}),
        )
        # and the turns well saved with ningu added
        self.assertNsEqual(
            ns(
                config.finalLoad,
                ningu=0
            ),
            ns(zip(
                minizinc.problem.names,
                minizinc.problem.maxLoad,
            )),
        )


    def test_indisponibilities(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        config = fixture()
        minizinc = Minizinc(config)
        # then we have the indisponibilities well formatted
        self.assertNsEqual(minizinc.busyReasons, """
            [dl, 0, goku]: Fight Freezer
            [dv, 0, goku]: Train
            [dm, 0, vegeta]: Date with Bulma
            [dx, 0, krilin]: Explode
            [dj, 0, krilin]: Resurect
        """)
        self.assertEqual(minizinc.problem.busy, [
            [{'goku'}],
            [{'vegeta'}],
            [{'krilin'}],
            [{'krilin'}],
            [{'goku'}],
        ])

    def test_undesired(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        config = fixture()
        minizinc = Minizinc(config)
        # then we have the undesired well formatted
        self.assertNsEqual(minizinc.undesiredReasons, """
            [dj, 0, goku]: Sleepy
            [dm, 0, krilin]: Eating
        """)
        self.assertEqual(minizinc.problem.undesired, [
            [set()],
            [{'krilin'}],
            [set()],
            [{'goku'}],
            [set()],
        ])

    def test_indisponibilities_with_holidays(self):
        config = fixture(
            monday=datetime.date(2023, 9, 11),
            # faked holiday on 2023-09-12, dm
        )
        minizinc = Minizinc(config)
        # busy does not includes busy in holiday
        self.assertNsEqual(minizinc.busyReasons, """
            [dl, 0, goku]: Fight Freezer
            [dv, 0, goku]: Train
            # this one is removed
            #[dm, 0, vegeta]: Date with Bulma
            [dx, 0, krilin]: Explode
            [dj, 0, krilin]: Resurect
        """)
        self.assertEqual(minizinc.problem.busy, [
            [{'goku'}],
            #[{'vegeta'}], # this one is removed
            [{'krilin'}],
            [{'krilin'}],
            [{'goku'}],
        ])

    def test_undesired(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        config = fixture()
        minizinc = Minizinc(config)
        # then we have the undesired well formatted
        self.assertNsEqual(minizinc.undesiredReasons, """
            [dj, 0, goku]: Sleepy
            [dm, 0, krilin]: Eating
        """)
        self.assertEqual(minizinc.problem.undesired, [
            [set()],
            [{'krilin'}],
            [set()],
            [{'goku'}],
            [set()],
        ])

    def test_undesired_withHolidays(self):
        config = fixture(
            monday=datetime.date(2023, 9, 11),
            # faked holiday on 2023-09-12, dm
        )
        minizinc = Minizinc(config)
        # then we have the undesired well formatted
        self.assertNsEqual(minizinc.undesiredReasons, """
            [dj, 0, goku]: Sleepy
        """)
        self.assertEqual(minizinc.problem.undesired, [
            [set()],
            [set()],
            [{'goku'}],
            [set()],
        ])

    def test_forcedTurns_whenMissing(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        nDays = 5 # week with no festivities
        config = fixture()
        minizinc = Minizinc(config)

        self.assertEqual(minizinc.problem.forced, [
            [set()],
            [set()],
            [set()],
            [set()],
            [set()],
        ])

    def test_forcedTurns_withAForcedTurn(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        day = 'dm'
        hour = 1
        line = 3 # ignored, just different from existing
        person = 'goku'
        config = fixture()
        config.forced = {
            (day, hour-1 , line): person
        }
        minizinc = Minizinc(config)
        self.assertEqual(minizinc.problem.forced, [
            [set()],
            [{'goku'}],
            [set()],
            [set()],
            [set()],
        ])

    def test_forcedTurns_withAForcedTurn_inAFestivity_ignored(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        day = 'dm'
        hour = 1
        line = 3 # ignored, just different from existing
        person = 'goku'
        config = fixture(
            monday=datetime.date(2023,9,11),
            # faked holiday on 2023-09-12, dm
        )
        config.forced = {
            (day, hour-1 , line): person
        }
        minizinc = Minizinc(config)
        expectation = [
            [set()],
            [set()],
            [set()],
            [set()],
        ]
        self.assertEqual(minizinc.problem.forced, expectation)

    def test_forcedTurns_withAMissingPerson(self):
        # Given a config with all the needed parameters
        # When we get a minizinc
        day = 'dm'
        hour = 1
        line = 3 # ignored, just different from existing
        person = 'mortadelo' # Not in Dragon Ball
        config = fixture()
        config.forced = {
            (day, hour-1 , line): person
        }
        minizinc = Minizinc(config)
        expectation = [
            [set()],
            [set()],
            [set()],
            [set()],
            [set()],
        ]
        self.assertEqual(minizinc.problem.forced, expectation)

    def solution(self, **override):
        return ns(solution=ns(ns(
            emptySlots=[],
            unforced=[],
            undesiredPenalties=[],
            concentratedLoad=[],
            discontinuousPenalties=[],
            farDiscontinuousPenalties=[],
            marathonPenalties=[],
            noBrunchPenalties=[],
            cost=10,
        ), **override))

    def scheduling(self, timetable, cost, **overrides):
        return ns(ns(
            week='2023-03-27',
            days=['dl', 'dm', 'dx', 'dj', 'dv'],
            hours=['8:00', '9:00'],
            turns=['L1', 'L2'],
            timetable=timetable,
            colors=[],
            extensions=[],
            names=[],
            overload={},
            penalties=[],
            cost=cost,
            log=[]
        ), **overrides)



    def test_translate(self):
        # Given a solution and a config
        config = fixture()
        minizinc = Minizinc(config)
        solution = self.solution(
            timetable=[
                [{'krilin', 'vegeta'}],  # dl
                [{'krilin', 'goku'}],  # dm
                [{'goku', 'vegeta'}],  # dx
                [{'goku', 'vegeta'}],  # dj
                [{'krilin', 'vegeta'}],  # dv
            ],
        )

        # When we call the minizinc translate method
        result = minizinc.translateSolution(solution)

        # Then we get the result as the expected namespace
        self.assertNsEqual(result, self.scheduling(
            timetable={
                'dl': [['krilin', 'vegeta']],
                'dm': [['goku', 'krilin']],
                'dx': [['goku', 'vegeta']],
                'dj': [['goku', 'vegeta']],
                'dv': [['krilin', 'vegeta']],
            },
            cost=10
        ))

    def test_translate__manyHours_singleLine(self):
        # Given a solution and a config
        config = fixture(
            nTelefons=1,
            hours=['9:00','10:00','11:00'],
        )
        minizinc = Minizinc(config)
        solution = self.solution(
            timetable=[
                [{'krilin'},{'vegeta'}],  # dl
                [{'krilin'},{'goku'}],  # dm
                [{'goku'},{'vegeta'}],  # dx
                [{'goku'},{'vegeta'}],  # dj
                [{'krilin'},{'vegeta'}],  # dv
            ],
        )

        # When we call the minizinc translate method
        result = minizinc.translateSolution(solution)

        # Then we get the result as the expected namespace
        self.assertNsEqual(result, self.scheduling(
            hours=['9:00','10:00','11:00'],
            timetable={
                'dl': [['krilin'],['vegeta']],
                'dm': [['krilin'],['goku']],
                'dx': [['goku'],['vegeta']],
                'dj': [['goku'],['vegeta']],
                'dv': [['krilin'],['vegeta']],
            },
            cost=10,
            turns=['L1'],
        ))

    def test_translate__nobodyMovedEnd(self):
        # Given a solution and a config
        config = fixture()
        minizinc = Minizinc(config)
        solution = self.solution(
            timetable=[
                [{'krilin', 'vegeta'}],  # dl
                [{'ningu', 'goku'}],  # dm
                [{'goku', 'vegeta'}],  # dx
                [{'ningu', 'vegeta'}],  # dj
                [{'krilin', 'vegeta'}],  # dv
            ],
        )

        # When we call the minizinc translate method
        result = minizinc.translateSolution(solution)

        # Then we get the result as the expected namespace
        self.assertNsEqual(result, self.scheduling(
            timetable={
                'dl': [['krilin', 'vegeta']],
                'dm': [['goku', 'ningu']], # this one
                'dx': [['goku', 'vegeta']],
                'dj': [['vegeta', 'ningu']], # this one
                'dv': [['krilin', 'vegeta']],
            },
            cost=10
        ))


    def test_translate__holesFilesWithNobody(self):
        # Given a solution and a config
        config = fixture()
        minizinc = Minizinc(config)
        solution = self.solution(
            timetable=[
                [{'krilin'}],  # dl
                [{'krilin', 'goku'}],  # dm
                [{'goku', 'vegeta'}],  # dx
                [{'goku'}],  # dj
                [{'krilin', 'vegeta'}],  # dv
            ],
        )

        # When we call the minizinc translate method
        result = minizinc.translateSolution(solution)

        # Filled with nobody
        self.assertNsEqual(result, self.scheduling(
            timetable={
                'dl': [['krilin', 'ningu']],
                'dm': [['goku', 'krilin']],
                'dx': [['goku', 'vegeta']],
                'dj': [['goku', 'ningu']],
                'dv': [['krilin', 'vegeta']]
            },
            cost=10
        ))

    def test_translate__festivitiesFilledIn(self):
        # Given a solution and a config with one holiday
        config = fixture(
            monday=datetime.date(2023,9,11),
            # faked holiday on 2023-09-12, dm
        )
        minizinc = Minizinc(config)
        minizinc.laborable_days = ['dl', 'dx', 'dj', 'dv']
        solution = self.solution(
            timetable=[
                [{'krilin'}],  # dl
                [{'krilin', 'goku'}],  # dx
                [{'goku', 'vegeta'}],  # dj
                [{'goku'}],  # dv
            ],
        )

        # When we call the minizinc translate method
        result = minizinc.translateSolution(solution)

        # Then we get the result as the expected namespace
        self.assertNsEqual(result, self.scheduling(
            week='2023-09-11',
            timetable={
                'dl': [['krilin', 'ningu']],
                'dm': [['festiu', 'festiu']], # this changes
                'dx': [['goku', 'krilin']],
                'dj': [['goku', 'vegeta']],
                'dv': [['goku', 'ningu']]
            },
            cost=10
        ))

    def assertPenalties(self, penalties, **overrides):
        # Given a solution and a config
        config = fixture(
            nTelefons=1,
            hours=['9:00','10:00','11:00'],
        )
        minizinc = Minizinc(config)
        solution = self.solution(
            timetable=[
                [{'krilin'},{'vegeta'}],  # dl
                [{'krilin'},{'goku'}],  # dm
                [{'goku'},{'vegeta'}],  # dx
                [{'goku'},{'vegeta'}],  # dj
                [{'krilin'},{'vegeta'}],  # dv
            ],
            **overrides
        )

        # When we call the minizinc translate method
        result = minizinc.translateSolution(solution)

        # Then we get the result as the expected namespace
        self.assertNsEqual(result, self.scheduling(
            hours=['9:00','10:00','11:00'],
            timetable={
                'dl': [['krilin'],['vegeta']],
                'dm': [['krilin'],['goku']],
                'dx': [['goku'],['vegeta']],
                'dj': [['goku'],['vegeta']],
                'dv': [['krilin'],['vegeta']],
            },
            cost=10,
            turns=['L1'],
            penalties=penalties,
        ))


    def test_translate__penalties_emptySlots(self):
        self.assertPenalties(
            emptySlots=[('dm', 1, 3)],
            penalties = [
                (900, '3 forats a dm 9:00 '),
            ],
        )

    def test_translate__penalties_undesired(self):
        self.assertPenalties(
            undesiredPenalties=[('dj', 1, 'goku')],
            penalties = [
                (5, 'goku dj 9:00 no li va be per: Sleepy'),
            ],
        )

    def test_translate__penalties_unforced(self):
        self.assertPenalties(
            unforced=[('dl', 1, 'goku')],
            penalties = [
                (50, 'dl 9:00 Torn fix no col·locat de goku'),
            ],
        )
    def test_translate__penalties_concentrated(self):
        n = 3
        self.assertPenalties(
            concentratedLoad=[('dm', 'goku', 3)],
            penalties = [
                (n*(n-1)*10, 'goku dm té 3 hores el mateix dia'),
            ],
        )

    def test_translate__penalties_discontinuous(self):
        self.assertPenalties(
            discontinuousPenalties=[('dl', 'krilin')],
            penalties = [
                (30, 'krilin dl té torns intercalats'),
            ],
        )
    def test_translate__penalties_farDiscontinuous(self):
        self.assertPenalties(
            farDiscontinuousPenalties=[('dl', 'krilin')],
            marathonPenalties=[],
            noBrunchPenalties=[],
            penalties = [
                (20, 'krilin dl té torns intercalats (als extrems)'),
            ],
        )

    def test_translate__penalties_noBrunch(self):
        self.assertPenalties(
            noBrunchPenalties=[('dl', 'krilin')],
            penalties = [
                (10, 'krilin dl no pot esmorzar'),
            ],
        )

    def test_translate__penalties_marathon(self):
        self.assertPenalties(
            marathonPenalties=[('dl', 'krilin')],
            penalties = [
                (40, 'krilin dl té 3 hores sense descans'),
            ],
        )

