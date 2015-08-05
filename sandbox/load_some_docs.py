# -*- coding: utf-8 -*-
"""
=============================================
Loading some documentation to the ML database
=============================================
"""
from __future__ import print_function, unicode_literals, absolute_import

from cStringIO import StringIO
import os

from mllib.documents import DocumentsService

if 'MLLIB_TEST_SERVER' not in os.environ:
    os.environ['MLLIB_TEST_SERVER'] = 'localhost:8000:admin:admin'

DOC_XML = b"""
<root>
  <uid>A00</uid>
  <title>A simple XML document</title>
  <content>
    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
    proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
  </content>
</root>
"""

uri = "sample1/sample2/doc1.xml"
ds = DocumentsService.from_envvar('MLLIB_TEST_SERVER')
ds.document_put(StringIO(DOC_XML), uri=uri)

print("A new document is at {}".format(uri))
answer = raw_input("Hit the return key to continue.")
