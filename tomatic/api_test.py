# -*- coding: utf-8 -*-

import copy
import unittest
from datetime import datetime
from mock import patch
import json
from pathlib import Path

from yamlns import namespace as ns
from . import api
from fastapi.testclient import TestClient
from .auth import validatedUser
from . import persons


def setNow(year,month,day,hour,minute):
    api.now=lambda:datetime(year,month,day,hour,minute)


@patch.dict('os.environ', TOMATIC_AUTH_DUMMY='vic')
class Api_Test(unittest.TestCase):
    from yamlns.testutils import assertNsEqual

    def setUp(self):
        self.maxDiff = None
        self.client = TestClient(api.app)
        api.app.dependency_overrides[validatedUser] = (
            lambda: dict(username='vic', email='me@here.coop')
        )

    def tearDown(self):
        del api.app.dependency_overrides[validatedUser]

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
        persons.persons("p.yaml")
        Path('p.yaml').write_text(u"""\
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
        persons.persons("p.yaml")
        Path('p.yaml').write_text(u"""\
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


if __name__ == "__main__":

    import sys
    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True

    unittest.main()

# vim: ts=4 sw=4 et
