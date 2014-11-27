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


'''
Entry API test cases for aggregator
'''

# unittest2 offers TestCase.assertMultiLineEqual that provide a nice
# diff output, sometimes it is called automagically by the old
# assertEqual


try:
    import unittest2 as unittest
except ImportError:
    # NOQA
    import unittest
import entry
from aggregator import app, db
from flask import json
import time

dumps = json.dumps
loads = json.loads

"""
    =========Entry API test cases=============
    Test cases for entry Api.
    Following request methods are supported by entry Api
        1. GET
        2. POST
        3. PUT
        4. DELETE
    Test cases for following API methods are added so far:
        1. GET (partial)
"""


class EntryTest(unittest.TestCase):

    id = ''
    entry_id = ''
    supported_params = {'title': entry.entry['title'],
                        'author': entry.entry['author']['slug'],
                        'tags': entry.entry['tags'][0]['slug'],
                        'related': entry.entry['related']['type']
                        + ',' + entry.entry['related']['id'],
                        'source': entry.entry['source']
                        }

    def setUp(self):
        self.app = app.test_client()
        self.createTestApiKey()

    def tearDown(self):
        db.apikey.remove({'key': app.config['API_KEY']})

    def createTestApiKey(self):
        data = {'key': app.config['API_KEY'], 'application': 'unit-test',
                'status': 1, 'created': int(time.time())}
        db.apikey.insert(data)

    def test_get_basic(self):
        """
            get_basic test case.
            This case will check for basic things like:
                1. entry get api is accessable our rest or not. response
                    status should be 200
                2. If entry Api is accessed without any paramater, it should
                    return following response
                    { status: "true", data: [] }
        """
        response = self.app.get('/api/v1/%s/json/entry' %
                                (app.config['API_KEY']))
        assert response.status_code == 200
        data = loads(response.data)
        assert data['status'] == 'true'
        assert data['data'] == []

    def test_get_api_version(self):
        """
            get_api_version test.
            Test case for testing supported Api version
        """
        supported_version = 'v1'
        unsupported_version = 'v2'
        response = self.app.get('/api/%s/%s/json/entry' %
                                (supported_version, app.config['API_KEY']))
        assert response.status_code == 200
        unsupported_call = self.app.get('/api/%s/%s/json/entry' %
                                        (unsupported_version,
                                         app.config['API_KEY']))
        assert unsupported_call.status_code == 404

    def test_get_api_key(self):
        """
           get_api_key test.
           Test case for testing valid Api key authentication check
        """
        valid_call = self.app.get('/api/v1/%s/json/entry' %
                                  (app.config['API_KEY']))
        assert valid_call.status_code == 200
        valid_call_data = loads(valid_call.data)
        assert valid_call_data['status'] == 'true'

        invalid_call = self.app.get('/api/v1/%s/json/entry' % ('invalidkey'))
        assert invalid_call.status_code == 200
        invalid_call_data = loads(invalid_call.data)
        assert invalid_call_data['status'] == 'false'

    def test_get_api_return_format(self):
        """
          get_api_return_format test
          Test case for testing supported return format defined
          in local_seetings
        """
        for format in app.config['ALLOWED_FORMATS']:
            response = self.app.get('/api/v1/%s/%s/entry' %
                                    (app.config['API_KEY'], format))
            assert response.status_code == 200
            data = loads(response.data)
            assert data['status'] == 'true'
        unsupported_format = 'string'
        unsupported_call = self.app.get('/api/v1/%s/%s/entry' %
                                        (app.config['API_KEY'],
                                         unsupported_format))
        assert unsupported_call.status_code == 200
        unsupported_call_data = loads(unsupported_call.data)
        assert unsupported_call_data['status'] == 'false'

    def test_get_api_parameters(self):
        """
          get_api_parameters test
          Test case for testing supported parameters
        """
        for param in list(self.supported_params):
            response = self.app.get('/api/v1/%s/json/entry?%s=%s&offset=0' %
                                    (app.config['API_KEY'], param, self.supported_params[param]))   # NOQA
            assert response.status_code == 200
            data = loads(response.data)
            if param == 'title':
                self.id = data['data'][0]['id']
                self.supported_params['id'] = self.id
                self.supported_params['range'] = self.id + ':1'
            assert data['status'] == 'true'

    def test_get_api_return_parameters(self):
        """
          get_api_return_parameters test
          Test case for testing supported return parameters
        """
        return_field = 'title, author, links'
        return_field_dict = return_field.split(', ')
        response = self.app.get('/api/v1/%s/json/entry?id=%s&return_fields=%s&offset=0' %  # NOQA
                                (app.config['API_KEY'], self.id, return_field))   # NOQA
        assert response.status_code == 200
        data = loads(response.data)
        assert len(data['data'][0]) == len(return_field_dict)
        return_field = set(data['data'][0])
        diffrence1 = [x for x in return_field_dict if x not in return_field]
        diffrence2 = [x for x in return_field if x not in return_field_dict]
        assert len(diffrence1) == 0
        assert len(diffrence2) == 0
        assert data['status'] == 'true'

    def test_get_api_enclosure_parameter(self):
        """
          get_api_enclosure_parameter test
          Test case for testing enclosure parameter
        """
        enclosures = 0
        return_field = 'title, author, links'
        response = self.app.get('/api/v1/%s/json/entry?id=%s&return_fields=%s&enclosures=%s&offset=0' %  # NOQA
                                (app.config['API_KEY'], self.id, return_field, enclosures))   # NOQA
        assert response.status_code == 200
        data = loads(response.data)
        if 'enclosures' in data['data'][0]['links']:
            raise AssertionError("condition failed")

    def test_post_basic(self):
        """
           post_basic test
        """
        invalid_post_data = {'title': 'hello'}
        valid_post_data = {'status': 'active', 'title': 'hello', 'content': {'description': 'testing post data'}, 'tags': [{'name': 'Technology', 'slug': 'technology'}], 'author': {'name': 'Test', 'slug': 'test'}}   # NOQA
        invalid_response = self.app.post('/api/v1/%s/json/entry' %
                                         (app.config['API_KEY']), data=dict(entry=dumps(invalid_post_data)))    # NOQA

        assert invalid_response.status_code == 200
        data = loads(invalid_response.data)
        assert data['data']['message'][0] == '104'

        valid_response = self.app.post('/api/v1/%s/json/entry' %
                                       (app.config['API_KEY']), data=dict(entry=dumps(valid_post_data)))    # NOQA

        assert valid_response.status_code == 200
        data = loads(valid_response.data)
        response = self.app.get('/api/v1/%s/json/entry?title=hello&offset=0' %
                                (app.config['API_KEY']))   # NOQA
        data = loads(response.data)
        EntryTest.id = data['data'][0]['id']

    def test_put_basic(self):
        """
           put_basic_test
        """
        invalid_put_data = {'title': 'update_hello', 'tags': [{'name': 'Technology', 'slug': 'technology'}, {'name': 'Testing', 'slug': 'testing'}]}  # NOQA
        valid_put_data = {'id': EntryTest.id, 'title': 'update_hello'}
        invalid_response = self.app.put('/api/v1/%s/json/entry' %
                                        (app.config['API_KEY']), data=dict(entry=dumps(invalid_put_data)))    # NOQA

        assert invalid_response.status_code == 200
        data = loads(invalid_response.data)
        assert data['data']['message'][0] == '111'

        valid_response = self.app.put('/api/v1/%s/json/entry' %
                                      (app.config['API_KEY']), data=dict(entry=dumps(valid_put_data)))    # NOQA

        assert valid_response.status_code == 200
        data = loads(valid_response.data)
        assert data['data'] == 'Entry updated'

    def test_updated_entry_delete_basic(self):
        """
           updated_entry_delete_test
        """
        delete_request = {'id': EntryTest.id}
        response = self.app.delete('/api/v1/%s/json/entry' %
                                   (app.config['API_KEY']), data=dumps(delete_request))   # NOQA
        assert response.status_code == 200
        delete_request = {'id': EntryTest.entry_id}
        response = self.app.delete('/api/v1/%s/json/entry' %
                                   (app.config['API_KEY']), data=dumps(delete_request))   # NOQA
        assert response.status_code == 200

    def test_check_empty_db(self):
        """
            check_empty_db_test
        """
        self.app.post('/api/v1/%s/json/entry' %
                      (app.config['API_KEY']), data=dict(entry=dumps(entry.entry)))    # NOQA

        response = self.app.get('/api/v1/%s/json/entry?title=TestEntry&offset=0' %                     # NOQA
                                (app.config['API_KEY']))   # NOQA
        data = loads(response.data)
        EntryTest.entry_id = data['data'][0]['id']
