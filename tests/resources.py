# -*- coding: utf-8 -*-
"""Misc fixtures and helpers for all tests"""
from __future__ import unicode_literals, print_function, absolute_import

import functools
import os

tests_directory = os.path.dirname(os.path.abspath(__file__))
tests_abs_path = functools.partial(os.path.join, tests_directory)

if 'MLLIB_TEST_SERVER' not in os.environ:
    os.environ['MLLIB_TEST_SERVER'] = 'localhost:8000:admin:admin'
