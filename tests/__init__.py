# -*- coding: utf-8 -*-
"""\
=====
mllib
=====

Tests package
"""
from __future__ import unicode_literals, print_function, absolute_import

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from .resources import tests_directory

def all_tests():
    return unittest.defaultTestLoader.discover(tests_directory)
