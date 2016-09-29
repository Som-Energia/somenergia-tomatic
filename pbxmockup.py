# -*- coding: utf-8 -*-

import unittest

class PbxMockup(object):
    """ """
    def currentQueue(self):
        """ """
        return []

class PbxMockup_Test(unittest.TestCase):
    
    def test_currentQueue_noConfiguration(self):
        pbx = PbxMockup()
        self.assertEqual(pbx.currentQueue(),
            [])
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
