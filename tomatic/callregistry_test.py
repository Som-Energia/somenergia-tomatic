import unittest
from pathlib import Path
from yamlns import namespace as ns
from datetime import date
from .callregistry import CallRegistry
from .persons import persons

def removeTree(path):
    path = Path(path)
    if not path.exists(): return
    if path.is_file():
        path.unlink()
        return
    for child in path.glob('*'):
        removeTree(child)
    path.rmdir()

class CallRegistry_Test(unittest.TestCase):
    def setUp(self):
        self.dir = Path('test_callregistry')
        removeTree(self.dir)
        self.dir.mkdir()
        self.dailycalls = self.dir / 'dailycalls.yaml'

    def tearDown(self):
        removeTree(self.dir)

    from yamlns.testutils import assertNsEqual

    def test_updateCall_behavesAtStartUp(self):
        reg = CallRegistry(self.dir)
        assert not (self.dir/'dailycalls.yaml').exists()
        self.assertEqual(reg.callsByUser('alice'), [])

    def test_updateCall_updatesAfterWrite(self):
        reg = CallRegistry(self.dir)
        reg.updateCall('alice', ns(
            attribute="value",
            tag="content",
        ))
        self.assertNsEqual(ns.load(self.dailycalls), """\
            alice:
            - attribute: value
              tag: content
        """)
        self.assertNsEqual(
            ns(calls = reg.callsByUser('alice')), """\
            calls:
            - attribute: value
              tag: content
        """)

    def test_updateCall_sameTimeExtension_updates(self):
        reg = CallRegistry(self.dir)
        reg.updateCall('alice', ns(
            data="2021-02-01T20:21:22.555Z",
            attribute="value",
            tag="content",
        ))
        reg.updateCall('alice', ns(
            data="2021-02-01T20:21:22.555Z",
            attribute="second value",
            tag="second content",
        ))
        self.assertNsEqual(ns.load(self.dailycalls), """\
            alice:
            - data: "2021-02-01T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)
        self.assertNsEqual(
            ns(calls = reg.callsByUser('alice')), """\
            calls:
            - data: "2021-02-01T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

    def test_updateCall_differentTime_appends(self):
        reg = CallRegistry(self.dir)
        reg.updateCall('alice', ns(
            data="2021-02-01T20:21:22.555Z",
            attribute="value",
            tag="content",
        ))
        reg.updateCall('alice', ns(
            data="2021-02-02T20:21:22.555Z",
            attribute="second value",
            tag="second content",
        ))
        self.assertNsEqual(ns.load(self.dailycalls), """\
            alice:
            - attribute: value
              tag: content
              data: "2021-02-01T20:21:22.555Z"
            - attribute: second value
              tag: second content
              data: "2021-02-02T20:21:22.555Z"
        """)
        self.assertNsEqual(
            ns(calls = reg.callsByUser('alice')), """\
            calls:
            - data: "2021-02-01T20:21:22.555Z"
              attribute: value
              tag: content
            - data: "2021-02-02T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

    def test_updateCall_differentExtension_splits(self):
        reg = CallRegistry(self.dir)

        reg.updateCall('alice', ns(
            data="2021-02-02T20:21:22.555Z",
            attribute="value",
            tag="content",
        ))
        reg.updateCall('barbara', ns(
            data="2021-02-02T20:21:22.555Z",
            attribute="second value",
            tag="second content",
        ))
        self.assertNsEqual(ns.load(self.dailycalls), """\
            alice:
            - data: "2021-02-02T20:21:22.555Z"
              attribute: value
              tag: content
            barbara:
            - data: "2021-02-02T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

        self.assertNsEqual(
            ns(calls = reg.callsByUser('alice')), """\
            calls:
            - data: "2021-02-02T20:21:22.555Z"
              attribute: value
              tag: content
        """)
        self.assertNsEqual(
            ns(calls = reg.callsByUser('barbara')), """\
            calls:
            - data: "2021-02-02T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

    def assertDirContent(self, expected):
        self.assertEqual(
            [str(x) for x in sorted(self.dir.glob('**/*'))],
            sorted(expected)
        )

    def test_appendDaily(self):
        reg = CallRegistry(self.dir)

        reg._appendToExtensionDailyInfo('prefix', ns(
            user="alice",
            date="2021-02-01T20:21:22.555Z",
            phone="555444333",
            partner="S00000",
            contract="100000",
            reason="CODE",
        ), date=date(2021,2,1))
        self.assertDirContent([
            'test_callregistry/prefix',
            'test_callregistry/prefix/20210201.yaml',
        ])
        self.assertNsEqual(ns.load('test_callregistry/prefix/20210201.yaml'),
            """
            alice:
            - date: "2021-02-01T20:21:22.555Z"
              phone: '555444333'
              partner: 'S00000'
              contract: '100000'
              reason: CODE
              user: alice
        """)

    def test_appendDaily_sameUserDateUpdates(self):
        reg = CallRegistry(self.dir)

        reg._appendToExtensionDailyInfo('prefix', ns(
            user="alice",
            date="2021-02-01T20:21:22.555Z",
            phone="555444333",
            partner="",
            contract="",
            reason="",
        ), date=date(2021,2,1))
        reg._appendToExtensionDailyInfo('prefix', ns(
            user="alice",
            date="2021-02-01T20:21:22.555Z",
            phone="555444333",
            partner="S00000",
            contract="100000",
            reason="CODE",
        ), date=date(2021,2,1))
        self.assertDirContent([
            'test_callregistry/prefix',
            'test_callregistry/prefix/20210201.yaml',
        ])
        self.assertNsEqual(ns.load('test_callregistry/prefix/20210201.yaml'),
            """
            alice:
            - date: "2021-02-01T20:21:22.555Z"
              phone: '555444333'
              partner: 'S00000'
              contract: '100000'
              reason: CODE
              user: alice
        """)


    def test_annotateCall_writesCallLog(self):
        reg = CallRegistry(self.dir)
        reg.annotateCall(ns(
            user="alice",
            date="2021-02-01T20:21:22.555Z",
            phone="555444333",
            partner="S00000",
            contract="100000",
            reason="CODE",
        ))
        content = ns.load(self.dailycalls)
        self.assertNsEqual(content, """\
            alice:
            - date: "2021-02-01T20:21:22.555Z"
              phone: '555444333'
              partner: 'S00000'
              contract: '100000'
              reason: CODE
        """)

    def test_annotateCall_writesFiles(self):
        reg = CallRegistry(self.dir)
        persons(self.dir/'persons.yaml')
        reg.annotateCall(ns(
            user="alice",
            date="2021-02-01T20:21:22.555Z",
            phone="555444333",
            partner="S00000",
            contract="100000",
            reason="CODE",
        ))
        self.assertDirContent([
            'test_callregistry/cases',
            'test_callregistry/cases/{:%Y%m%d}.yaml'.format(
                date.today()),
            str(self.dailycalls),
        ])


