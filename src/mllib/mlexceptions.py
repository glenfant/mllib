# -*- coding: utf-8 -*-
"""
==================
mllib.mlexceptions
==================
"""

from __future__ import unicode_literals, print_function, absolute_import

import json


class MarkLogicServerError(Exception):
    """An error that must be used for response status codes 4xx and 5xx.
    This assumes that we always provide the ``X-Error-Accept`` header with
    every REST request.

    See http://docs.marklogic.com/guide/rest-dev/intro#id_34966
    """
    def __init__(self, response):
        """Initializer

        :param response: a :class:`requests.Response` object with server error code
        """
        self.http_code = response.status_code
        if response.headers['content-type'].startswith('application/json'):
            # Making the message from the response
            self.json_msg = json.loads(response.text).get('errorResponse', {})
        else:
            self.json_msg = {}
        self.mlcode = self.json_msg.get('messageCode', '(Unknown code)')
        self.mlmessage = self.json_msg.get('message', '(Unknown message)')

    def __str__(self):
        return "HTTP code {0} ({1}): {2}".format(self.http_code, self.mlcode, self.mlmessage)
