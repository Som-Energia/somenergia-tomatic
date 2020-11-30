import unittest
from . import persons
from pathlib2 import Path
from yamlns import namespace as ns

class Persons_Test(unittest.TestCase):

    from yamlns.testutils import assertNsEqual

    def setUp(self):
        ''


    def tearDown(self):
        persons.persons(False)

    def test_persons_explicitPath(self):
        Path('p.yaml').write_text(u"hola: tu")
        ps = persons.persons('p.yaml')
        self.assertNsEqual(ps, """\
            hola: tu
        """)
        self.assertEqual(persons.persons.path, Path('p.yaml'))

    def test_persons_defaultPath(self):
        ps = persons.persons()
        self.assertEqual(persons.persons.path, 
            (Path(__file__) / '../../persons.yaml').resolve()
        )

    def test_persons_cached(self):
        Path('p.yaml').write_text(u"hola: tu")
        persons.persons('p.yaml')
        persons.persons.cache = ns.loads("ni: yo")
        ps = persons.persons()
        self.assertNsEqual(ps, """\
            ni: yo
        """)

    def test_persons_falseInvalidatesCache(self):
        Path('p.yaml').write_text(u"hola: tu")
        persons.persons('p.yaml')
        persons.persons.cache = ns.loads("ni: yo")
        ps = persons.persons(False)
        self.assertEqual(ps, None)
        ps = persons.persons('p.yaml')
        self.assertNsEqual(ps, """\
            hola: tu
        """)

    def test_persons_updated(self):
        Path('p.yaml').write_text(u"hola: tu")
        persons.persons('p.yaml')
        import time
        time.sleep(1) # TODO: use ns 
        Path('p.yaml').write_text(u"hola: you")
        ps = persons.persons()
        self.assertNsEqual(ps, """\
            hola: you
        """)

    def test_persons_differentPath(self):
        Path('p.yaml').write_text(u"hola: tu")
        Path('p2.yaml').write_text(u"hola: yo")
        persons.persons('p.yaml')
        ps = persons.persons('p2.yaml')
        self.assertNsEqual(ps, """\
            hola: yo
        """)

    def test_byExtension(self):
        Path('p.yaml').write_text(u"""\
            extensions:
                me: "6666"
            """)
        persons.persons('p.yaml')
        self.assertEqual(
            persons.byExtension('6666'),
            'me')
        self.assertEqual(
            persons.byExtension('1111'),
            '1111')

    def test_name(self):
        Path('p.yaml').write_text(u"""\
            names:
                jm: Jose Miguel
            """)

        persons.persons('p.yaml')
        self.assertEqual(
            persons.name('jm'),
            'Jose Miguel')

        self.assertEqual(
            persons.name('missing'),
            'Missing')

    def test_name_withoutNames(self):
        Path('p.yaml').write_text(u"""\
            {}
            """)

        persons.persons('p.yaml')
        self.assertEqual(
            persons.name('jm'),
            'Jm')

        self.assertEqual(
            persons.name('missing'),
            'Missing')
        
    def test_nameByExtension(self):
        Path('p.yaml').write_text(u"""\
            extensions:
                jm: "6666"
            names:
                jm: Jose Miguel
            """)

        persons.persons('p.yaml')
        self.assertEqual(
            persons.nameByExtension('6666'),
            'Jose Miguel')

        


# vim: et ts=4 sw=4
