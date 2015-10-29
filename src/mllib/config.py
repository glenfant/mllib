# -*- coding: utf-8 -*-
"""
============
mllib.config
============

Some configuration globals
"""
from __future__ import unicode_literals, print_function, absolute_import

import sys

DEFAULT_CHARSET = 'utf-8'
DEBUG = False  # Do NOT commit/push with "True"
HAVE_PYTHON3 = sys.version_info[0] == 3
UNKNOWN_MIMETYPE = 'application/octet-stream'
STREAM_LINE_MAX_SIZE = 100000  # Max allowed size for each line when reading a multipart/mixed response
