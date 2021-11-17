import unittest
from pathlib import Path
from .callregistry import CallRegistry
from yamlns import namespace as ns

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
        reg = CallRegistry(self.dailycalls)
        assert not (self.dir/'dailycalls.yaml').exists()
        self.assertEquals(reg.callsByExtension('alice'), [])

    def test_updateCall_updatesAfterWrite(self):
        reg = CallRegistry(self.dailycalls)
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
            ns(calls = reg.callsByExtension('alice')), """\
            calls:
            - attribute: value
              tag: content
        """)

    def test_updateCall_sameTimeExtension_updates(self):
        reg = CallRegistry(self.dailycalls)
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
            ns(calls = reg.callsByExtension('alice')), """\
            calls:
            - data: "2021-02-01T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

    def test_updateCall_differentTime_appends(self):
        reg = CallRegistry(self.dailycalls)
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
            ns(calls = reg.callsByExtension('alice')), """\
            calls:
            - data: "2021-02-01T20:21:22.555Z"
              attribute: value
              tag: content
            - data: "2021-02-02T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

    def test_updateCall_differentExtension_splits(self):
        reg = CallRegistry(self.dailycalls)

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
            ns(calls = reg.callsByExtension('alice')), """\
            calls:
            - data: "2021-02-02T20:21:22.555Z"
              attribute: value
              tag: content
        """)
        self.assertNsEqual(
            ns(calls = reg.callsByExtension('barbara')), """\
            calls:
            - data: "2021-02-02T20:21:22.555Z"
              attribute: second value
              tag: second content
        """)

        



