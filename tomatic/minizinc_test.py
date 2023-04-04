# -*- encoding: utf-8 -*-
import unittest
import datetime
from unittest.mock import patch

from yamlns import namespace as ns

from .minizinc import Menu
from .minizinc import solve_problem

# TODO: real fixture ?
def fixture():
    return ns(
        monday=datetime.datetime(2023, 3, 27),
        idealLoad=ns(
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

class Menu_Test(unittest.TestCase):
    from somutils.testutils import assertNsEqual

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
        given_persons = list(config.idealLoad.keys())
        shuffled_persons = menu.names
        # then we have the persons shuffled
        self.assertEqual(len(shuffled_persons), len(given_persons))
        for person in given_persons:
            self.assertIn(person, shuffled_persons)
        # and the turns well saved
        for i, torns in enumerate(menu.nTorns):
            name = menu.names[i]
            ideal_load = config.idealLoad[name]
            self.assertEqual(ideal_load, torns)

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

    @patch("tomatic.busy.laborableWeekDays")
    def test_indisponibilities_with_holidays(self, mocked_laborableWeekDays):
        # Given a config with a monday of a week with holidays (friday)
        config = fixture()
        config.monday = datetime.date(2023, 4, 3)
        mocked_laborableWeekDays.return_value = ['dl', 'dm', 'dx', 'dj']
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
        # When we call the menu translate method
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
        expected = ns(
            week='2023-03-27 00:00:00',
            days=['dl', 'dm', 'dx', 'dj', 'dv'],
            hours=['8:00', '9:00'],
            turns=['T1', 'T2'],
            timetable={
                'dl': [['vegeta', 'krilin']],
                'dm': [['goku', 'krilin']],
                'dx': [['goku', 'vegeta']],
                'dj': [['goku', 'vegeta']],
                'dv': [['vegeta', 'krilin']]
            },
            colors=[],
            extensions=[],
            names=[],
            overload={},
            penalties=[],
            cost=10,
            log=[]
        )
        # Then we get the result as the expected namespace
        result = menu.translate(solution, config)
        self.assertNsEqual(expected, result)


class Minizinc_Test(unittest.TestCase):

    def test_solve_problem_ok(self):
        # Given well formatted config
        # When we call the solve problem method
        config = fixture()
        solution = solve_problem(config, ['chuffed', 'coin-bc'])
        # Then we have a solution
        self.assertNotEqual(False, solution)
        # self.assertEqual({}, solution)

    def test_solve_problem_ko(self):
        # Given well formatted config but no solution
        config = fixture()
        config.idealLoad.goku = 1
        # When we call the solve problem method
        solution = solve_problem(config, ['chuffed', 'coin-bc'])
        # Then we do not have a solution
        self.assertFalse(solution)
