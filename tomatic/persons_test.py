import unittest
from . import persons
from pathlib import Path
from yamlns import namespace as ns

def safeRemove(filename):
    f = Path(filename)
    if f.exists():
        f.unlink()

class Persons_Test(unittest.TestCase):

    from yamlns.testutils import assertNsEqual

    def setUp(self):
        ''


    def tearDown(self):
        persons.persons(False)
        safeRemove('p.yaml')
        safeRemove('p2.yaml')

    def test_persons_explicitPath(self):
        Path('p.yaml').write_text(u"hola: tu")
        ps = persons.persons('p.yaml')
        self.assertNsEqual(ps, """\
            hola: tu
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
        """)
        self.assertEqual(persons.persons.path, Path('p.yaml'))

    def test_persons_defaultPath(self):
        expectedDefaultPath = (Path(__file__) / '../../persons.yaml').resolve()
        ps = persons.persons()
        self.assertEqual(persons.persons.path, expectedDefaultPath)

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
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
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
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
        """)

    def test_persons_differentPath(self):
        Path('p.yaml').write_text(u"hola: tu")
        Path('p2.yaml').write_text(u"hola: yo")
        persons.persons('p.yaml')
        ps = persons.persons('p2.yaml')
        self.assertNsEqual(ps, """\
            hola: yo
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
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

    def test_extension_whenPresent(self):
        Path('p.yaml').write_text(u"""\
            extensions:
                jm: "6666"
            """)

        persons.persons('p.yaml')
        self.assertEqual(
            persons.extension('jm'),
            '6666')

    def test_extension_missingPerson(self):
        Path('p.yaml').write_text(u"""\
            extensions:
                jm: "6666"
            """)

        persons.persons('p.yaml')
        self.assertEqual(
            persons.extension('missing'),
            None)

    def test_extension_noExtensions(self):
        Path('p.yaml').write_text(u"""\
            {}
            """)

        persons.persons('p.yaml')
        self.assertEqual(
            persons.extension('missing'),
            None)

    def test_update_nameAndBasics(self):
        Path('p.yaml').write_text(u"""\
                extensions:
                  someone: '777'
                  someother: '222'
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            name = 'namevalue',
            extension = '666',
            table = 4,
            color = '00ff00',
            email = 'name@home.com',
            erpuser = 'ErpUser',
        ))
        self.assertNsEqual(persons.persons(), """\
            names:
              someone: namevalue
            erpusers:
              someone: ErpUser
            extensions:
              someone: '666' # overwritten
              someother: '222' # kept
            tables:
              someone: 4
            colors:
              someone: 00ff00
            emails:
              someone: name@home.com
            groups: {}
            loads: {}
        """)

    def test_update_groups_addedNew(self):
        Path('p.yaml').write_text(u"""\
                names: {}
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            groups = ['mygroup']
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            extensions: {}
            erpusers: {}
            tables: {}
            colors: {}
            emails: {}
            groups:
              mygroup:
              - someone
            loads: {}
        """)

    def test_update_groups_addedExisting(self):
        Path('p.yaml').write_text(u"""\
            groups:
              mygroup:
              - anotherone
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            groups = ['mygroup']
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            extensions: {}
            erpusers: {}
            tables: {}
            colors: {}
            emails: {}
            groups:
              mygroup:
              - anotherone
              - someone
            loads: {}
        """)

    def test_update_groups_removeGroup(self):
        Path('p.yaml').write_text(u"""\
            groups:
              mygroup:
              - someone
              - someother
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            groups = []
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups:
              mygroup:
              - someother
            loads: {}
        """)


    def test_update_groups_removeLastMemberOfGroup(self):
        Path('p.yaml').write_text(u"""\
            groups:
              mygroup:
              - someone
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            groups = []
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
        """)

    def test_update_groups_existingGroups_untouched(self):
        Path('p.yaml').write_text(u"""\
            groups:
              mygroup:
              - someone
              othergroup:
              - other
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            groups = []
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups:
              othergroup:
              - other
            loads: {}
        """)

    def test_update_groups_existingGroups_keepGroups(self):
        Path('p.yaml').write_text(u"""\
            groups:
              mygroup:
              - someone
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            groups = ['mygroup']
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups:
              mygroup:
              - someone
            loads: {}
        """)

    def test_update_load_adds(self):
        Path('p.yaml').write_text(u"""\
                names: {}
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            load = 7,
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            extensions: {}
            erpusers: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads:
              someone: 7
        """)

    def test_update_load_toNone_removes(self):
        Path('p.yaml').write_text(u"""\
                names: {}
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            load = 7,
        ))
        persons.update('someone', ns(
            load = None,
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            extensions: {}
            erpusers: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
        """)

    def test_update_load_unset_keeps(self):
        Path('p.yaml').write_text(u"""\
                names: {}
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            load = 7,
        ))
        persons.update('someone', ns(
            extension='555',
        ))
        self.assertNsEqual(persons.persons(), """\
            names: {}
            extensions:
                someone: '555'
            erpusers: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads:
                someone: 7
        """)

    def test_update_getSaved(self):
        Path('p.yaml').write_text(u"""\
                extensions: {}
            """)
        persons.persons('p.yaml')
        persons.update('someone', ns(
            extension = '666',
        ))

        self.assertNsEqual(ns.load('p.yaml'), """\
            names: {}
            erpusers: {}
            extensions:
              someone: '666' # overwritten
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
        """)

    def test_persons_explicit(self):
        persons.persons('p.yaml')
        p = persons.persons()
        self.assertNsEqual(p, """
            names: {}
            erpusers: {}
            extensions: {}
            tables: {}
            colors: {}
            emails: {}
            groups: {}
            loads: {}
        """)

# vim: et ts=4 sw=4
