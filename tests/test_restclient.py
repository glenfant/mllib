# -*- coding: utf-8 -*-
"""
==========================
Testing mllib.mlexceptions
==========================
"""

from __future__ import unicode_literals, print_function, absolute_import

import json
import unittest

import requests

from mllib.restclient import RESTClient
from mllib.mlexceptions import MarkLogicServerError


class RestClientTest(unittest.TestCase):
    """Base client class dor REST operations
    Tests may use services from https://httpbin.org/
    """
    @classmethod
    def setUpClass(cls):
        cls.client = RESTClient('httpbin.org', 80, 'schtroumpf', 'schtroumpf')

    def test_rest_get(self):
        """RESTClient.rest_get()"""
        params = {'foo': 'bar'}
        response = self.client.rest_get('/get', params=params)
        self.assertTrue(response.ok)
        body = json.loads(response.content)
        self.assertDictEqual(body['args'], params)
        self.assertDictContainsSubset({'X-Error-Accept': b'application/json'}, body['headers'])

    def test_rest_post(self):
        """RESTClient.rest_post()"""
        self._test_rest_send_verb(self.client.rest_post, '/post')

    def test_rest_patch(self):
        """RESTClient.rest_patch()"""
        self._test_rest_send_verb(self.client.rest_patch, '/patch')

    def test_rest_put(self):
        """RESTClient.rest_put()"""
        self._test_rest_send_verb(self.client.rest_put, '/put')

    def test_rest_delete(self):
        """RESTClient.rest_delete()"""
        self._test_rest_send_verb(self.client.rest_delete, '/delete')

    def _test_rest_send_verb(self, req_func, path):
        """Common test for several http verbs"""
        params = {'foo': 'bar'}
        data = {'one': 'two'}
        response = req_func(path, params=params, data=data)
        self.assertTrue(response.ok)
        body = json.loads(response.content)
        self.assertDictEqual(body['args'], params)
        self.assertDictContainsSubset({'X-Error-Accept': b'application/json'}, body['headers'])
        self.assertDictContainsSubset(data, body['form'])

    def test_rest_exception(self):
        """Raise and inspect a MarklogicServerError"""
        client = RESTClient.from_envvar('MLLIB_TEST_SERVER')
        with self.assertRaises(MarkLogicServerError) as ctxt:
            client.rest_get('/v1/documents', params={'uri': 'nonexistent.xml'})
        exc = ctxt.exception
        self.assertEqual(exc.http_code, 404)
        self.assertEqual(exc.mlcode, 'RESTAPI-NODOCUMENT')

    def test_authentication(self):
        """Digest authentication passes"""
        response = self.client.rest_get('/digest-auth/auth/schtroumpf/schtroumpf')
        self.assertTrue(response.ok)
        self.assertDictEqual(response.json(), {'authenticated': True, 'user': 'schtroumpf'})

