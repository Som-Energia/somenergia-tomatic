import unittest
import pydantic
import datetime
from .dummy import CallRegistry
from .models import CallLog, NewCall, Call
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

    call_alice3 = ns(
        operator = 'alice',
        call_timestamp = "2020-01-03T00:00:00+00:00",
        pbx_call_id = "2020-01-03T00:00:00+00:00-555444333-bababa",
        phone_number = "444333222",
        comments = "holi",
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
        return response.updated_id

    def assertModelEqual(self, model, expected):
        self.assertNsEqual(model.model_dump(), expected)

    def assertCallList(self, response, expectedCalls):
        self.assertModelEqual(response, ns(calls=[
            self.full_call(id, call)
            for id, call in expectedCalls
        ]))

    def setUp(self):
        self.maxDiff = None
        self.path = self.enterContext(temp_path())
        self.registry = CallRegistry(self.path)
        return super().setUp()

    # Categories

    def test__categories__when_none_available_empty_list(self):
        response = self.registry.categories()
        self.assertModelEqual(response, ns(categories=[
        ]))

    def test__categories__full_category(self):
        (self.path / "call_registry" / "categories.yaml").write_text("""
        categories:
        - id: 1
          name: Category with all fields
          code: mycategory
          keywords: ["akeyword"]
          color: "#eeaaee"
          enabled: false
          levels: []
        """)
        response = self.registry.categories()
        self.assertModelEqual(response, """
        categories:
        - id: 1
          name: Category with all fields
          code: mycategory
          keywords: ["akeyword"]
          color: "#eeaaee"
          enabled: false
          levels: []
        """)


    def test__categories__default_fields_are_filled(self):
        (self.path / "call_registry" / "categories.yaml").write_text("""
        categories:
        - id: 1
          name: Category just with mandatory fields
          code: mycategory
          levels: []
        """)
        response = self.registry.categories()
        self.assertModelEqual(response, """
        categories:
        - id: 1
          name: Category just with mandatory fields
          code: mycategory
          keywords: []
          color: null
          enabled: true
          levels: []
        """)

    # Registering incomming calls

    def test__get_calls__when_no_call_registered__returns_empty(self):
        response = self.registry.get_calls('alice')
        self.assertCallList(response, [
            # No calls
        ])

    def test__get_calls__after_adding_one__returns_it(self):
        odoo_id = self.register(self.call_alice1)

        response = self.registry.get_calls('alice')

        self.assertCallList(response,[ 
            (odoo_id, self.call_alice1),
        ])

    def test__get_calls__is_persistent_between_instances(self):
        odoo_id = self.register(self.call_alice1)

        # Using a different CallRegistry
        other_registry = CallRegistry(self.path)
        response = other_registry.get_calls('alice')

        self.assertCallList(response, [
            (odoo_id, self.call_alice1),
        ])

    def test__get_calls__after_adding_many__returns_them(self):
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_alice2)

        response = self.registry.get_calls('alice')
        self.assertCallList(response, [
            (odoo_id1, self.call_alice1),
            (odoo_id2, self.call_alice2),
        ])

    def test__get_calls__other_operators_calls_not_listed(self):
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_barbara)

        response = self.registry.get_calls('alice')
        self.assertCallList(response, [
            (odoo_id1, self.call_alice1),
            # barbara call filltered out
        ])

        response = self.registry.get_calls('barbara')
        self.assertCallList(response, [
            # alice call filltered out
            (odoo_id2, self.call_barbara),
        ])

        response = self.registry.get_calls('carol')
        self.assertCallList(response, [
            # alice call filltered out
            # barbara call filltered out
        ])

    def test__get_calls__ids_are_unique_among_operators(self):
        # Fixes bug: each operator had their own sequence
        # so ids were not unique
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_barbara)
        self.assertNotEqual(odoo_id1, odoo_id2)

    # Call modification

    def test__modify_existing_call__with_only_one_call(self):
        # given a single registered call
        odoo_id1 = self.register(self.call_alice1)
        # we obtain back the list of calls
        calls = self.registry.get_calls('alice').calls
        # we choose the only call we have
        edited_call = calls[0]
        # and edit some of its fields fields
        edited_call.comments = 'New comment'
        edited_call.category_ids = [2]

        # when we modify the value of the fields
        response = self.registry.modify_existing_call(edited_call)

        # then we get back the list of calls with the modification
        self.assertModelEqual(response, ns(
            updated_id = edited_call.id,
            calls = [
                edited_call.model_dump(),
            ],
        ))

    def test__modify_existing_call__with_many_calls__changes_the_one_of_matching_id(self):
        # given many registered calls for an operator
        odoo_id1 = self.register(self.call_alice1)
        odoo_id2 = self.register(self.call_alice2)
        # we obtain back the list of calls
        calls = self.registry.get_calls('alice').calls
        # we choose to edit the second one
        unmodified_call = calls[0]
        edited_call = calls[1]
        # and edit edit some fields
        edited_call.comments = 'New comment'
        edited_call.category_ids = [2]

        # when we modify the value of the fields
        response = self.registry.modify_existing_call(edited_call)

        # then we get back the list of calls with the modification
        self.assertModelEqual(response, ns(
            updated_id = edited_call.id,
            calls = [
                unmodified_call.model_dump(),
                edited_call.model_dump(),
            ],
        ))

    def test__modify_existing_call__when_id_not_found__issues_error(self):  self.skipTest("Not yet implemented")
    def test__modify_existing_call__when_operator_changed__issues_error(self):  self.skipTest("Not yet implemented")


