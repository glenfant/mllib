# -*- coding: utf-8 -*-
"""
=======================
Transactions management
=======================

Demo with transactions commiting / aborting
"""
from __future__ import print_function, unicode_literals, absolute_import

import json
import logging
import os
from StringIO import StringIO

from mllib.documents import DocumentsService
from mllib.transactions import TransactionsService

logging.basicConfig(level=logging.WARNING)  # Try "INFO" then "DEBUG" for more verbosity


def hit_return():
    raw_input("\nHit [Return] to continue:")

if 'MLLIB_TEST_SERVER' not in os.environ:
    os.environ['MLLIB_TEST_SERVER'] = 'localhost:8000:admin:admin'

LOREM_IPSUM = b"""
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
DOC_JSON = {
    'uid': 'A01',
    'title': "A simple JSON document",
    'content': LOREM_IPSUM
}
DOC_JSON = json.dumps(DOC_JSON, ensure_ascii=True)

# Starting a transaction and get its id

ds = DocumentsService.from_envvar('MLLIB_TEST_SERVER')
ts = TransactionsService.from_envvar('MLLIB_TEST_SERVER')

txid = ts.transactions_post(name='kiki', timeLimit=444)

# Checking the status of that transaction

tx_info = ts.transactions_txid_get(txid)

# Check we retrieve the provided information

status = tx_info['transaction-status']
assert status['transaction-id'] == txid
assert status['transaction-name'] == 'kiki'
assert status['time-limit'] == u'444'  # Why ML dos not provide a float or int ?


print("Our transaction id is", txid)
print("Creating a document within this transaction")
hit_return()

uri = "python_demo/sample1/doc2.json"
ds.document_put(StringIO(DOC_JSON), uri=uri, txid=txid)


print("Document created but should not show in the query console (did not yet commit)")

