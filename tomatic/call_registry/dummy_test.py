import unittest
from .dummy import CallRegistry
from ..callregistry_models import CallLog
from somutils.testutils import temp_path
from yamlns import ns

class DummyTest(unittest.TestCase):
    from yamlns.testutils import assertNsEqual

    def test__get_calls__when_no_call_registered(self):
        with temp_path() as path:
            registry = CallRegistry(path)
            response: CallLog = registry.get_calls('alice')
            self.assertNsEqual(ns(response.model_dump()), """
                operator_calls: []
            """)
