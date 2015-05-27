# -*- coding: utf-8 -*-
"""
==========================
Testing mllib.mlexceptions
==========================
"""

from __future__ import unicode_literals, print_function, absolute_import

import unittest

import requests

from mllib.restclient import RESTClient
from mllib.mlexceptions import MarkLogicServerError

class MLExceptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = RESTClient.from_envvar('MLLIB_TEST_SERVER')

    def test_exccontent(self):
        headers = {
            'X-Error-Accept': b'application/json',
            'Accept': b'application/xml'
        }
        endpoint = self.client.base_url + '/v1/documents'
        params = {'uri': 'nonexistent.xml'}
        response = requests.get(endpoint, params=params, headers=headers, auth=self.client.authentication)
        self.assertFalse(response.ok)

        exc = MarkLogicServerError(response)
        self.assertEqual(exc.mlcode, 'RESTAPI-NODOCUMENT')
        self.assertIn('nonexistent.xml', exc.mlmessage)



