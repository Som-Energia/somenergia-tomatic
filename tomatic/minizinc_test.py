# -*- encoding: utf-8 -*-
import unittest
import datetime
from unittest.mock import patch

from yamlns import namespace as ns

from .minizinc import Menu
from .minizinc import solve_problem
from .busy import weekdays as fullWeekdays
from pathlib import Path


# TODO: real fixture ?
def fixture():
    return ns(
        monday=datetime.datetime(2023, 3, 27),
        idealLoad=ns(
            goku=4,
            vegeta=4,
            krilin=4,
        ),
        finalLoad=ns(
            goku=4,
            vegeta=4,
            krilin=4,
        ),
        nTelefons=2,
        hours=['8:00', '9:00'],
        nNingusMinizinc=0,
        maximHoresDiariesGeneral=2,
        busyTable={
            ('dl', 0, 'goku'): 'Fight Freezer',
            ('dm', 0, 'goku'): False,
            ('dx', 0, 'goku'): False,
            ('dj', 0, 'goku'): False,
            ('dv', 0, 'goku'): 'Train',
            ('dl', 0, 'vegeta'): False,
            ('dm', 0, 'vegeta'): 'Date with Bulma',
            ('dx', 0, 'vegeta'): False,
            ('dj', 0, 'vegeta'): False,
            ('dv', 0, 'vegeta'): False,
            ('dl', 0, 'krilin'): False,
            ('dm', 0, 'krilin'): False,
            ('dx', 0, 'krilin'): 'Explote',
            ('dj', 0, 'krilin'): 'Resurect',
            ('dv', 0, 'krilin'): False,
        },
        colors=[],
        extensions=[],
        names=[],
    )


def make_minizinc_ns_result(timetable, cost):
    return ns(
        week='2023-03-27 00:00:00',
        days=['dl', 'dm', 'dx', 'dj', 'dv'],
        hours=['8:00', '9:00'],
        turns=['T1', 'T2'],
        timetable=timetable,
        colors=[],
        extensions=[],
        names=[],
        overload={},
        penalties=[],
        cost=cost,
        log=[]
    )


class Menu_Test(unittest.TestCase):
    from somutils.testutils import assertNsEqual

    def setUp(self):
        self.todelete=[]
        self.holidaysfile = Path('holidays.conf')
        self.oldholidays = None
        if self.holidaysfile.exists():
            self.oldholidays = self.holidaysfile.read_text(encoding='utf8')
        self.holidaysfile.write_text(
            "2020-12-24\tNadal\n"
            "2020-12-25\tNadal\n"
            "2020-12-26\tNadal\n"
            "",
            encoding='utf8',
        )

    def tearDown(self):
        for filename in self.todelete:
            os.remove(filename)
        if self.oldholidays is None:
            self.holidaysfile.unlink()
        else:
            self.holidaysfile.write_text(
                self.oldholidays, encoding='utf8')

    def test_create_menu_instance(self):
        # Given a config with all the needed paramenters
        # when we initialize a Menu
        config = fixture()
        menu = Menu(config)
        # then we have an instance of Menu
        self.assertIsInstance(menu, Menu)

    def test_shuffle_persons(self):
        # Given a config with all the needed parameters
        # When we get a menu
        config = fixture()
        menu = Menu(config)
        given_persons = list(config.finalLoad.keys())
        shuffled_persons = menu.names
        # then we have the persons shuffled
        self.assertEqual(len(shuffled_persons), len(given_persons))
        for person in given_persons:
            self.assertIn(person, shuffled_persons)
        # and the turns well saved
        for i, torns in enumerate(menu.nTorns):
            name = menu.names[i]
            full_load = config.finalLoad[name]
            self.assertEqual(full_load, torns)

    def test_indisponibilities(self):
        # Given a config with all the needed parameters
        # When we get a menu
        config = fixture()
        menu = Menu(config)
        # then we have the indisponibilities well formatted
        indisponibilities = {  # indisponibilities per person
            'goku': [{1}, set(), set(), set(), {1}],
            'vegeta': [set(), {1}, set(), set(), set()],
            'krilin': [set(), set(), {1}, {1}, set()],
        }
        expected_indisponibilities = []
        for name in menu.names:  # to sort considering the shuffle result
            expected_indisponibilities.extend(
                indisponibilities[name]
            )
        self.assertEqual(expected_indisponibilities, menu.indisponibilitats)

    def test_forcedTurns_whenMissing(self):
        # Given a config with all the needed parameters
        # When we get a menu
        nDays = 5 # week with no festivities
        config = fixture()
        menu = Menu(config)

        self.assertEqual(menu.forcedTurns, [
            set()
            for _ in range(len(config.finalLoad) * nDays)
        ])

    def test_forcedTurns_withAForcedTurn(self):
        # Given a config with all the needed parameters
        # When we get a menu
        nDays = 5 # week with no festivities
        day = 'dm'
        iday = fullWeekdays.index(day)
        person = 'goku'
        hour = 1
        line = 3
        config = fixture()
        config.forced = {
            (day, hour-1 , line): 'goku'
        }
        menu = Menu(config)
        expectation = [
            set()
            for idx in range(len(config.finalLoad) * nDays)
        ]
        iperson = menu.names.index(person)
        expectation[iday + nDays*iperson] = {hour}

        self.assertEqual(menu.forcedTurns, expectation)

    @patch("tomatic.minizinc.laborableWeekDays")
    def test_forcedTurns_withAForcedTurn_inAFestivity_ignored(self, mocked_laborableWeekDays):
        mocked_laborableWeekDays.return_value = ['dl', 'dx', 'dj', 'dv'] # dm removed
        # Given a config with all the needed parameters
        # When we get a menu
        nDays = 4 # week with a festivity
        day = 'dm'
        iday = fullWeekdays.index(day)
        person = 'goku'
        hour = 1
        line = 3
        config = fixture()
        config.forced = {
            (day, hour-1 , line): 'goku'
        }
        menu = Menu(config)
        expectation = [
            set()
            for idx in range(len(config.finalLoad) * nDays)
        ]
        self.assertEqual(menu.forcedTurns, expectation)

    @patch("tomatic.minizinc.laborableWeekDays")
    def test_indisponibilities_with_holidays(self, mocked_laborableWeekDays):
        mocked_laborableWeekDays.return_value = ['dl', 'dm', 'dx', 'dj']
        # Given a config with a monday of a week with holidays (friday)
        config = fixture()
        config.monday = datetime.date(2023, 4, 3)
        # When we get a menu
        menu = Menu(config)
        # then we have the indisponibilities without the holiday
        indisponibilities = {  # indisponibilities per person
            'goku': [{1}, set(), set(), set()],
            'vegeta': [set(), {1}, set(), set()],
            'krilin': [set(), set(), {1}, {1}],
        }
        expected_indisponibilities = []
        for name in menu.names:  # to sort considering the shuffle result
            expected_indisponibilities.extend(
                indisponibilities[name]
            )
        self.assertEqual(expected_indisponibilities, menu.indisponibilitats)

    def test_translate(self):
        # Given a solution and a config
        config = fixture()
        menu = Menu(config)
        menu.names = ['goku', 'vegeta', 'krilin']
        solution = ns(
            solution=ns(
                ocupacioSlot=[
                    [{3, 2}],  # dl
                    [{3, 1}],  # dm
                    [{1, 2}],  # dx
                    [{1, 2}],  # dj
                    [{3, 2}],  # dv
                ],
                totalTorns=10
            )
        )

        # When we call the menu translate method
        result = menu.translate(solution, config)

        # Then we get the result as the expected namespace
        expected = make_minizinc_ns_result(
            timetable={
                'dl': [['vegeta', 'krilin']],
                'dm': [['goku', 'krilin']],
                'dx': [['goku', 'vegeta']],
                'dj': [['goku', 'vegeta']],
                'dv': [['vegeta', 'krilin']]
            },
            cost=10
        )
        self.assertNsEqual(expected, result)


    def test_translate_with_ningus(self):
        # Given a solution and a config
        config = fixture()
        menu = Menu(config)
        menu.names = ['goku', 'vegeta', 'krilin']
        solution = ns(
            solution=ns(
                ocupacioSlot=[
                    [{3}],  # dl
                    [{3, 1}],  # dm
                    [{1, 2}],  # dx
                    [{1}],  # dj
                    [{3, 2}],  # dv
                ],
                totalTorns=10
            )
        )

        # When we call the menu translate method
        result = menu.translate(solution, config)

        # Then we get the result as the expected namespace
        expected = make_minizinc_ns_result(
            timetable={
                'dl': [['krilin', 'ningu']],
                'dm': [['goku', 'krilin']],
                'dx': [['goku', 'vegeta']],
                'dj': [['goku', 'ningu']],
                'dv': [['vegeta', 'krilin']]
            },
            cost=10
        )
        self.assertNsEqual(expected, result)


    def test_translate_with_holidays(self):
        # Given a solution and a config with one holiday
        config = fixture()
        menu = Menu(config)
        menu.names = ['goku', 'vegeta', 'krilin']
        menu.laborable_days = ['dl', 'dm', 'dx', 'dv']
        solution = ns(
            solution=ns(
                ocupacioSlot=[
                    [{3}],  # dl
                    [{3, 1}],  # dm
                    [{1, 2}],  # dx
                    [{1}],  # dv
                ],
                totalTorns=8
            )
        )

        # When we call the menu translate method
        result = menu.translate(solution, config)

        # Then we get the result as the expected namespace
        expected = make_minizinc_ns_result(
            timetable={
                'dl': [['krilin', 'ningu']],
                'dm': [['goku', 'krilin']],
                'dx': [['goku', 'vegeta']],
                'dj': [['ningu', 'ningu']],
                'dv': [['goku', 'ningu']]
            },
            cost=8
        )
        self.assertNsEqual(expected, result)


class Minizinc_Test(unittest.TestCase):

    def setUp(self):
        self.todelete=[]
        self.holidaysfile = Path('holidays.conf')
        self.oldholidays = None
        if self.holidaysfile.exists():
            self.oldholidays = self.holidaysfile.read_text(encoding='utf8')
        self.holidaysfile.write_text(
            "2020-12-24\tNadal\n"
            "2020-12-25\tNadal\n"
            "2020-12-26\tNadal\n"
            "",
            encoding='utf8',
        )

    def tearDown(self):
        for filename in self.todelete:
            os.remove(filename)
        if self.oldholidays is None:
            self.holidaysfile.unlink()
        else:
            self.holidaysfile.write_text(
                self.oldholidays, encoding='utf8')

    def test_solve_problem_ok(self):
        # Given well formatted config
        config = fixture()
        # When we call the solve problem method
        solution = solve_problem(config, ['chuffed', 'coin-bc'])
        # Then we have a solution
        self.assertNotEqual(False, solution)
        # self.assertEqual({}, solution)

    def test_solve_problem_ko(self):
        # Given well formatted config but no solution
        config = fixture()
        config.finalLoad.goku = 1
        # When we call the solve problem method
        solution = solve_problem(config, ['chuffed', 'coin-bc'])
        # Then we do not have a solution
        self.assertFalse(solution)
