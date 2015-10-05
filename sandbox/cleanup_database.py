# -*- coding: utf-8 -*-
"""
===============================
Cleaning up your tests database
===============================
"""
from __future__ import print_function, unicode_literals, absolute_import

import json
import os

from mllib.documents import DocumentsService
from mllib.eval import EvalService

ALL_URIS_JS = r"""
var res = [];
for (var x of fn.doc()) {
  res.push(fn.documentUri(x))
    }
res;
"""

def hit_return():
    raw_input("\nHit [Return] to continue:")

if 'MLLIB_TEST_SERVER' not in os.environ:
    os.environ['MLLIB_TEST_SERVER'] = 'localhost:8000:admin:admin'
print("Warning, your database will be cleaned")
hit_return()

es = EvalService.from_envvar('MLLIB_TEST_SERVER')
ds = DocumentsService.from_envvar('MLLIB_TEST_SERVER')
response = es.eval_post(javascript=ALL_URIS_JS)
headers, document = response.iter_parts().next()
uris = json.loads(document)
ds.document_delete(uri=uris)
