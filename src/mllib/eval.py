# -*- coding: utf-8 -*-
"""
==========
mllib.eval
==========

http://docs.marklogic.com/REST/POST/v1/eval
"""

from __future__ import unicode_literals, print_function, absolute_import

import json

from .restclient import RESTClient
from .utils import KwargsSerializer, ResponseAdapter, dict_pop


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
        headers = {'Accept': 'multipart/mixed', 'Content-type': 'application/x-www-form-urlencoded'}
        data = dict_pop(params, 'xquery', 'javascript', 'vars')
        if 'vars' in data:
            data['vars'] = json.dumps(dict(data['vars']))
        response = self.rest_post('/v1/eval', params=params, data=data, headers=headers)
        return ResponseAdapter(response)
