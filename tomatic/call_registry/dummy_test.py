import unittest
from .dummy import CallRegistry
from .models import CallLog, NewCall
from somutils.testutils import temp_path
from yamlns import ns

class DummyTest(unittest.TestCase):
    from yamlns.testutils import assertNsEqual
    from somutils.testutils import enterContext

    def setUp(self):
        self.maxDiff = None
        self.path = self.enterContext(temp_path())
        self.registry = CallRegistry(self.path)
        return super().setUp()

    def assertModelEqual(self, model, expected):
        self.assertNsEqual(model.model_dump(), expected)

    def test__get_calls__when_no_call_registered__returns_empty(self):
        response = self.registry.get_calls('alice')
        self.assertModelEqual(response, """
            operator_calls: []
        """)

    def test__get_calls__after_adding_one__returns_it(self):
        response = self.registry.add_incoming_call(NewCall(
            operator = 'alice',
            call_timestamp = "2020-01-01T00:00:00.000Z",
            pbx_call_id = "2020-01-01T00:00:00.000Z-666555444-edade5",
            phone_number = "666555444",
        ))
        odoo_id = response.odoo_id
        response = self.registry.get_calls('alice')
        self.assertModelEqual(response, f"""
            operator_calls:
            - id: {odoo_id}
              operator: alice
              call_timestamp: 2020-01-01T00:00:00.000Z
              pbx_call_id: 2020-01-01T00:00:00.000Z-666555444-edade5
              phone_number: "666555444"
              caller_erp_id: null
              caller_vat: ''
              caller_name: ''
              contract_erp_id: null
              contract_number: ''
              contract_address: ''
              category_ids: []
              comments: ''
        """)

    def test__get_calls__is_persistent_between_instances(self):
        self.registry.add_incoming_call(NewCall(
            operator = 'alice',
            call_timestamp = "2020-01-01T00:00:00.000Z",
            pbx_call_id = "2020-01-01T00:00:00.000Z-666555444-edade5",
            phone_number = "666555444",
        ))
        other_registry = CallRegistry(self.path)
        response = other_registry.get_calls('alice')
        self.assertModelEqual(response, """
            operator_calls:
            - id: 1
              operator: alice
              call_timestamp: 2020-01-01T00:00:00.000Z
              pbx_call_id: 2020-01-01T00:00:00.000Z-666555444-edade5
              phone_number: "666555444"
              caller_erp_id: null
              caller_vat: ''
              caller_name: ''
              contract_erp_id: null
              contract_number: ''
              contract_address: ''
              category_ids: []
              comments: ''
        """)

    def test__get_calls__after_adding_many__returns_them(self):
        response1 = self.registry.add_incoming_call(NewCall(
            operator = 'alice',
            call_timestamp = "2020-01-01T00:00:00.000Z",
            pbx_call_id = "2020-01-01T00:00:00.000Z-666555444-edade5",
            phone_number = "666555444",
        ))
        odoo_id1 = response1.odoo_id

        response2 = self.registry.add_incoming_call(NewCall(
            operator = 'alice',
            call_timestamp = "2020-01-02T00:00:00.000Z",
            pbx_call_id = "2020-01-02T00:00:00.000Z-555444333-bababa",
            phone_number = "555444333",
        ))
        odoo_id2 = response2.odoo_id

        response = self.registry.get_calls('alice')
        self.assertModelEqual(response, f"""
            operator_calls:
            - id: {odoo_id1}
              operator: alice
              call_timestamp: 2020-01-01T00:00:00.000Z
              pbx_call_id: 2020-01-01T00:00:00.000Z-666555444-edade5
              phone_number: "666555444"
              caller_erp_id: null
              caller_vat: ''
              caller_name: ''
              contract_erp_id: null
              contract_number: ''
              contract_address: ''
              category_ids: []
              comments: ''
            - id: {odoo_id2}
              operator: alice
              call_timestamp: 2020-01-02T00:00:00.000Z
              pbx_call_id: 2020-01-02T00:00:00.000Z-555444333-bababa
              phone_number: "555444333"
              caller_erp_id: null
              caller_vat: ''
              caller_name: ''
              contract_erp_id: null
              contract_number: ''
              contract_address: ''
              category_ids: []
              comments: ''
        """)

    def test__get_calls__other_operators_calls_not_listed(self): self.skipTest("Not yet implemented")
    def test__typify_call__modifies_existing_call(self):  self.skipTest("Not yet implemented")
    def test__typify_call__manual_call__creates_a_new_call(self):  self.skipTest("Not yet implemented")

