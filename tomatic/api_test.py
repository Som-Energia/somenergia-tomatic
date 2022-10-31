# -*- coding: utf-8 -*-

import copy
import unittest
from datetime import datetime
from mock import patch

from yamlns import namespace as ns
from . import api
from fastapi.testclient import TestClient


def setNow(year,month,day,hour,minute):
    api.now=lambda:datetime(year,month,day,hour,minute)

class Api_Test(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.client = TestClient(api.app)

    @patch("tomatic.api.schedulestorage.Storage.load")
    @patch("tomatic.api.schedulestorage.Storage.save")
    def test_editSlot_baseCase(self, mocked_saver, mocked_loader):
        # Given a time table
        old_time_table = ns(
            hours=['09:00', '10:15'],
            turns=['L1', 'L2'],
            timetable=ns(
                dl=[
                    ['vic', 'cire', 'carme'],
                    ['vic', 'cire', 'carme'],
                ]
            )
        )
        mocked_loader.return_value = old_time_table
        day = 'dl'
        hour_index = 0
        turn_index = 0
        name = 'cire'

        # When we change one person in time table
        response = self.client.patch(
            '/api/graella/2022-10-31/{}/{}/{}/{}'.format(
                day, hour_index, turn_index, name
            ),
            json="vic"
        )

        # The request was success
        self.assertEquals(response.status_code, 200)
        # and API saves the time table with change applied
        new_time_table = copy.deepcopy(old_time_table)
        new_time_table.timetable[day][hour_index][turn_index] = name
        mocked_saver.assert_called_with(new_time_table)


if __name__ == "__main__":

    import sys
    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True

    unittest.main()

# vim: ts=4 sw=4 et
