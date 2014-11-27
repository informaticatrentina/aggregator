# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author: Santosh Singh <santosh@incaendo.com>
#
# This file is part of the aggregator project.
#
# This file can not be copied and/or distributed without the express
# permission of <ahref Foundation.
#
###############################################################################


'''api key model test cases for aggregator
'''

# unittest2 offers TestCase.assertMultiLineEqual that provide a nice
# diff output, sometimes it is called automagically by the old
# assertEqual


try:
    import unittest2 as unittest
except ImportError:
    # NOQA
    import unittest
from aggregator import app
from flask import json
from ..api_key import APIKeyHandler

dumps = json.dumps
loads = json.loads


class APIKeyTest(unittest.TestCase):
    """Test case for api_key model
    """
    def setUp(self):
        """Setup api_key test env
            Create a test DB
        """
        app.config['TESTING'] = True

    def tearDown(self):
        """Getrid of test databases everytime
        """
        pass

    def test_api_key(self):
        """api_key model test case
            Insert and assert test api keys
        """
        apikeyobj = APIKeyHandler()
        test_app_name = 'testing'
        api_key_id = apikeyobj.save(test_app_name)
        test_api_key_data = apikeyobj.loadKey(str(api_key_id))
        assert test_app_name == test_api_key_data['application']
        apikeyobj.delete(str(api_key_id))
