# -*- coding: utf-8 -*-

import copy
import unittest
from datetime import datetime
from mock import patch
import json
from pathlib import Path

from yamlns import namespace as ns
from fastapi.testclient import TestClient
from somutils.testutils import temp_path
from . import api
from .auth import validatedUser
from . import persons
from .testutils import environ
from .call_registry.dummy import CallRegistry
from .call_registry.models import NewCall, Call

def setNow(year,month,day,hour,minute):
    api.now=lambda:datetime(year,month,day,hour,minute)


@patch.dict('os.environ', TOMATIC_AUTH_DUMMY='vic')
class Api_Test(unittest.TestCase):
    from yamlns.testutils import assertNsEqual
    from somutils.testutils import enterContext

    def setUp(self):
        self.maxDiff = None
        self.data_path = self.enterContext(temp_path())
        self.enterContext(environ("TOMATIC_CALLREGISTRY", 'dummy'))
        self.enterContext(environ("TOMATIC_DATA_PATH", str(self.data_path)))
        self.client = TestClient(api.app)
        api.app.dependency_overrides[validatedUser] = (
            lambda: dict(username='vic', email='me@here.coop')
        )

    def setupPersons(self, content):
        persons.persons(self.data_path/'persons.yaml')
        Path(self.data_path/'persons.yaml').write_text(content)

    def tearDown(self):
        del api.app.dependency_overrides[validatedUser]

    def model_yaml(self, model):
        return ns(model.model_dump(mode='json')).dump().encode('utf-8'),

    def assertResponseEqual(self, response, data, status=200):
        if type(data) == str:
            data = ns.loads(data)

        self.assertNsEqual(
            ns(
                yaml=ns.loads(response.text),
                status=response.status_code,
            ),
            ns(
                yaml=data,
                status=status,
            ),
        )

    def getTimeTableObjectStructure(self, time_table):
        return ns(
            hours=['09:00', '10:15'],
            turns=['L1', 'L2'],
            timetable=ns(time_table)
        )

    def test_persons_delete_whenNotAdmin(self):
        self.setupPersons(u"""\
            emails:
              vic: me@here.coop
              superwoman: kara.danvers@kripton.space
            groups:
              admin:
              - superwoman
        """)
        response = self.client.delete(
            '/api/person/superwoman',
        )
        self.assertResponseEqual(response, """
            detail: Only admins can perform this operation
        """, 403)

    def test_persons_delete_whenAdmin(self):
        self.setupPersons("""\
            emails:
              vic: me@here.coop
              kara: kara.danvers@kripton.space
            groups:
              admin:
              - vic
        """)
        response = self.client.delete(
            '/api/person/kara',
        )
        self.assertResponseEqual(response, """
            persons:
                colors: {}
                erpusers: {}
                extensions: {}
                idealloads: {}
                names: {}
                tables: {}
                emails:
                    vic: me@here.coop
                    # kara was removed
                groups:
                    admin:
                    - vic
        """, 200)

    @patch("tomatic.api.schedulestorage.Storage.load")
    @patch("tomatic.api.schedulestorage.Storage.save")
    @patch("tomatic.api.schedulestorage.utcnow",
        lambda: datetime(2023,2,23,18,11,32,386313)
    )
    def test_editSlot_baseCase(self, mocked_saver, mocked_loader):
        # Given a time table
        old_time_table = self.getTimeTableObjectStructure({
            'dl': [
                ['vic', 'cire', 'carme'],
                ['vic', 'cire', 'carme'],
            ]
        })
        mocked_loader.return_value = old_time_table
        day = 'dl'
        hour_index = 0
        turn_index = 0
        name = 'cire'

        expected = copy.deepcopy(old_time_table)
        expected.timetable[day][hour_index][turn_index] = name
        expected.overload=ns(
            vic= -1,
            cire= 1,
        )
        expected.log = [
            '2023-02-23 18:11:32.386313: vic ha canviat dl 09:00-10:15 L1 de vic a cire'
        ]

        # When we change one person in time table
        response = self.client.patch(
            '/api/graella/2022-10-31/{}/{}/{}/{}'.format(
                day, hour_index, turn_index, name
            ),
        )


        # The request was success
        self.assertResponseEqual(response, expected)
        # and API saves the time table with change applied
        mocked_saver.assert_called_with(expected)

    @patch("tomatic.api.schedulestorage.Storage.load")
    @patch("tomatic.api.schedulestorage.Storage.save")
    def test_editSlot_ningusLimit(self, mocked_saver, mocked_loader):
        # Given a time table
        old_time_table = self.getTimeTableObjectStructure({
            'dl': [
                ['vic', 'ningu', 'ningu'],
                ['vic', 'ningu', 'ningu'],
            ]
        })
        mocked_loader.return_value = old_time_table
        day = 'dl'
        hour_index = 0
        turn_index = 0
        name = 'ningu'

        # When we change one person in time table
        response = self.client.patch(
            '/api/graella/2022-10-31/{}/{}/{}/{}'.format(
                day, hour_index, turn_index, name
            ),
            json="vic"
        )

        # API returns 400 error
        # with a message of the error that occurred
        self.assertResponseEqual(response, """
            error: Hi ha masses Ningu en aquest torn
        """, 400)


    def test__callinfo_ringring__post(self):
        self.setupPersons("""\
            extensions:
              vic: "200"
        """)

        response = self.client.post(
            '/api/info/ringring',
            data=dict(
                ext="200",
                phone="567567567",
                callid="",
            )
        )
        self.assertResponseEqual(response, """
            result: ok
        """)

        registry = CallRegistry(self.data_path)
        calls = registry.get_calls('vic')
        self.assertEqual(len(calls.calls), 1)

    def test__callinfo_ringring__get(self):
        self.setupPersons("""\
            extensions:
              vic: "200"
        """)

        response = self.client.get(
            '/api/info/ringring',
            params=dict( # by query params
                extension="200", # This name diverges from post
                phone="567567567",
                callid="",
            )
        )
        self.assertResponseEqual(response, """
            result: ok
        """)

        registry = CallRegistry(self.data_path)
        calls = registry.get_calls('vic')
        self.assertEqual(len(calls.calls), 1)

    def test__call_categories(self):
        (self.data_path / "call_registry").mkdir()
        (self.data_path / "call_registry" / "categories.yaml").write_text("""
            categories:
            - id: 1
              name: Category with all fields
              code: mycategory
              keywords: ["akeyword"]
              color: "#eeaaee"
              levels:
              - level 1
              - level 2
        """)

        response = self.client.get('/api/call/categories')

        self.assertResponseEqual(response, """
            categories:
            - id: 1
              name: Category with all fields
              code: mycategory
              keywords: ["akeyword"]
              color: "#eeaaee"
              enabled: true
              levels:
              - level 1
              - level 2
        """)

    def test__call_log__when_empty(self):
        response = self.client.get('/api/call/log')
        self.assertResponseEqual(response, """
            calls: []
        """)

    def test__call_log__with_calls(self):
        self.setupPersons("""\
            extensions:
              vic: "200"
        """)
        response = self.client.get(
            '/api/info/ringring',
            params=dict( # by query params
                extension="200", # This name diverges from post
                phone="567567567",
                callid="",
            )
        )

        response = self.client.get('/api/call/log')

        data = ns.loads(response.text)
        calls = data.get("calls", [])
        id = calls[0].get('id', "ID not informed")
        call_timestamp = calls[0].get('call_timestamp', "call_timestamp not informed")
        pbx_call_id = calls[0].get('pbx_call_id', "pbx_call_id not informed")
        self.assertResponseEqual(response, f"""
            calls:
            - call_timestamp: {call_timestamp}
              caller_erp_id: null
              caller_name: ''
              caller_vat: ''
              category_ids: []
              comments: ''
              contract_address: ''
              contract_erp_id: null
              contract_number: ''
              id: {id}
              operator: vic
              pbx_call_id: {pbx_call_id}
              phone_number: '567567567'
        """)

    def test__annotate_manual_call(self):
        call = NewCall(
            call_timestamp="2020-02-02T02:02:02Z",
            pbx_call_id='my_pbx_id',
            phone_number='567567567',
            category_ids= [1,2],
            comments= '',
            operator='vic',
        )


        response = self.client.post('/api/call/annotate',
            data=self.model_yaml(call),
        )

        data = ns.loads(response.text)
        calls = data.get("calls", [])
        id = data.get('updated_id', 'updated_id not informed')
        call_timestamp = calls[0].get('call_timestamp', "call_timestamp not informed")
        self.assertResponseEqual(response, f"""
            updated_id: {id}
            calls:
            - call_timestamp: {call_timestamp}
              caller_erp_id: null
              caller_name: ''
              caller_vat: ''
              category_ids: [1,2]
              comments: ''
              contract_address: ''
              contract_erp_id: null
              contract_number: ''
              id: {id}
              operator: vic
              pbx_call_id: 'my_pbx_id'
              phone_number: '567567567'
        """)

    def test__annotate_existing_call(self):
        # Given an existing call
        existing_call = NewCall(
            call_timestamp="2020-02-02T02:02:02Z",
            pbx_call_id='my_pbx_id',
            phone_number='567567567',
            operator='vic',
        )
        response = self.client.post('/api/call/annotate',
            data=self.model_yaml(existing_call)
        )
        data = ns.loads(response.text)
        id = data.updated_id
        saved_existing_call = data.calls[0]

        # When we annotate the call
        edited_call = Call(
            **dict(
                saved_existing_call,
                category_ids= [1,2],
                comments= '',
            )
        )
        response = self.client.put('/api/call/annotate', # POST->PUT is different
            data=self.model_yaml(edited_call),
        )

        # Then the call is updated with the annotation
        data = ns.loads(response.text)
        calls = data.get("calls", [])
        call_timestamp = saved_existing_call.call_timestamp
        self.assertResponseEqual(response, f"""
            updated_id: {id}
            calls:
            - call_timestamp: {call_timestamp}
              caller_erp_id: null
              caller_name: ''
              caller_vat: ''
              category_ids: [1,2]
              comments: ''
              contract_address: ''
              contract_erp_id: null
              contract_number: ''
              id: {id}
              operator: vic
              pbx_call_id: 'my_pbx_id'
              phone_number: '567567567'
        """)

if __name__ == "__main__":

    import sys
    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True

    unittest.main()

# vim: ts=4 sw=4 et
