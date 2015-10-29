# -*- coding: utf-8 -*-
"""
==================
mllib.transactions
==================

http://docs.marklogic.com/REST/client/transaction-management
Manages transactions on documents handling
"""

from __future__ import unicode_literals, print_function, absolute_import

import json

from .restclient import RESTClient
from .utils import KwargsSerializer, guess_mimetype, is_sequence, ResponseAdapter


class TransactionsService(RESTClient):

    def transactions_post(self, **kwargs):
        """Create a multi-statement transaction. The resulting transaction id may
        be used in the txid request parameter of subsequent requests to force
        evaluation to take place in the context of the created transaction.
        http://docs.marklogic.com/REST/POST/v1/transactions

        :param kwargs: Named arguments from the dict ``requirements`` below
        :return: A transaction identifier usable as "txid" parameter for all compatible REST commands or None (error)
        """
        requirements = {
            'name': '?',
            'timeLimit': '?',
            'database': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)
        headers = {'Content-Type': b'text/plain', 'Accept': 'application/json'}
        response = self.rest_post('/v1/transactions', params=params, headers=headers, allow_redirects=False)
        assert response.status_code == 303, "We expected a 303 HTTP status code"
        location_hdr = response.headers['Location']
        return location_hdr.rsplit('/', 1)[-1]

    def transactions_txid_get(self, txid, **kwargs):
        """Retrieve status information for the transaction whose id matches the txid given in the request URI.
        http://docs.marklogic.com/REST/GET/v1/transactions/%5Btxid%5D

        :param kwargs: Named arguments from the dict ``requirements`` below
        :return:
        """
        requirements = {
            'format': '?',
            'database': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)

        # Default format will be JSON
        if 'format' not in params:
            params['format'] = 'json'
            headers = {'Accept': 'application/json'}
        response = self.rest_get('/v1/transactions/{0}'.format(txid), params=params, headers=headers)
        return json.loads(response.text)
