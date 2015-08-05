# -*- coding: utf-8 -*-
"""
==========
mllib.eval
==========

http://docs.marklogic.com/REST/POST/v1/eval
"""

from __future__ import unicode_literals, print_function, absolute_import

from .restclient import RESTClient
from .utils import KwargsSerializer


class EvalService(RESTClient):
    def eval_post(self, **kwargs):
        requirements = {
            'xquery': '?',
            'javascript': '?',
            'vars': '?',
            'database': '?',
            'txid': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)
        response = self.rest_post('/v1/eval', params=params)
        return response
