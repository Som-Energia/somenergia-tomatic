import unittest
import pydantic
import datetime
from .dummy import CallRegistry
from .models import CallLog, NewCall
from somutils.testutils import temp_path
from yamlns import ns

class DummyTest(unittest.TestCase):
    from yamlns.testutils import assertNsEqual
    from somutils.testutils import enterContext

    call_alice1 = ns(
        operator = 'alice',
        call_timestamp = "2011-11-04T00:05:23+00:00",
        pbx_call_id = "2020-01-01T00:00:00+00::00-666555444-edade5",
        phone_number = "666555444",
    )

    call_alice2 = ns(
        operator = 'alice',
        call_timestamp = "2020-01-02T00:00:00+00:00",
        pbx_call_id = "2020-01-02T00:00:00+00:00-555444333-bababa",
        phone_number = "555444333",
    )

    call_barbara = ns(
        operator = 'barbara',
        call_timestamp = "2020-01-03T00:00:00+00:00",
        pbx_call_id = "2020-01-03T00:00:00+00:00-555444333-bababa",
        phone_number = "444333222",
    )

    default_fields = ns(
        caller_erp_id = None,
        caller_vat = '',
        caller_name = '',
        contract_erp_id = None,
        contract_number = '',
        contract_address = '',
        category_ids = [],
        comments = '',
    )

    def full_call(self, id, data):
        call_timestamp = datetime.datetime.fromisoformat(data.call_timestamp)
        data = ns(data, call_timestamp = call_timestamp)
        return ns(self.default_fields, id=id, **data)

    def register(self, call):
        response = self.registry.add_incoming_call(
            NewCall(**call),
        )
        return response.odoo_id

    def setUp(self):
        self.maxDiff = None
        self.path = self.enterContext(temp_path())
        self.registry = CallRegistry(self.path)
        return super().setUp()

    def assertModelEqual(self, model, expected):
        self.assertNsEqual(model.model_dump(), expected)


    def test__get_calls__when_no_call_registered__returns_empty(self):
        response = self.registry.get_calls('alice')
        self.assertModelEqual(response, ns(operator_calls=[
            # No calls
        ]))

    def test__get_calls__after_adding_one__returns_it(self):
        odoo_id = self.register(self.call_alice1)

        response = self.registry.get_calls('alice')

        self.assertModelEqual(response, ns(operator_calls=[
            self.full_call(odoo_id, self.call_alice1),
        ]))

    def test__get_calls__is_persistent_between_instances(self):
        odoo_id = self.register(self.call_alice1)

        # Using a different CallRegistry
        other_registry = CallRegistry(self.path)
        response = other_registry.get_calls('alice')

        self.assertModelEqual(response, ns(operator_calls=[
            self.full_call(odoo_id, self.call_alice1),
        ]))

    def test__get_calls__after_adding_many__returns_them(self):
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_alice2)

        response = self.registry.get_calls('alice')
        self.assertModelEqual(response, ns(operator_calls=[
            self.full_call(odoo_id1, self.call_alice1),
            self.full_call(odoo_id2, self.call_alice2),
        ]))

    def test__get_calls__other_operators_calls_not_listed(self):
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_barbara)

        response = self.registry.get_calls('alice')
        self.assertModelEqual(response, ns(operator_calls=[
            self.full_call(odoo_id1, self.call_alice1),
            # barbara call filltered out
        ]))

        response = self.registry.get_calls('barbara')
        self.assertModelEqual(response, ns(operator_calls=[
            # alice call filltered out
            self.full_call(odoo_id2, self.call_barbara),
        ]))

        response = self.registry.get_calls('carol')
        self.assertModelEqual(response, ns(operator_calls=[
            # alice call filltered out
            # barbara call filltered out
        ]))

    def test__get_calls__ids_are_unique_among_operators(self):
        # Fixes bug: each operator had their own sequence
        # so ids were not unique
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_barbara)
        self.assertNotEqual(odoo_id1, odoo_id2)


    def test__typify_call__modifies_existing_call(self):  self.skipTest("Not yet implemented")
    def test__typify_call__manual_call__creates_a_new_call(self):  self.skipTest("Not yet implemented")


