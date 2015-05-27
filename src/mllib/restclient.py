# -*- coding: utf-8 -*-
"""
================
mllib.restserver
================


Global REST server access
"""

from __future__ import unicode_literals, print_function, absolute_import

import os
from functools import partial as ft_partial

import requests.auth
import requests

from .mlexceptions import MarkLogicServerError


class RESTClient(object):
    def __init__(self, hostname, port, username, password, authtype='digest'):
        auth_methods = {
            'basic': requests.auth.HTTPBasicAuth,
            'digest': requests.auth.HTTPDigestAuth,
        }
        auth_method = auth_methods.get(authtype, requests.auth.HTTPDigestAuth)
        self.base_url = 'http://{0}:{1}'.format(hostname, port)
        self.authentication = auth_method(username, password)
        self.rest_get = ft_partial(self.rest_do, 'get')
        self.rest_post = ft_partial(self.rest_do, 'post')
        self.rest_patch = ft_partial(self.rest_do, 'patch')
        self.rest_put = ft_partial(self.rest_do, 'put')
        self.rest_delete = ft_partial(self.rest_do, 'delete')

    @classmethod
    def from_envvar(cls, varname):
        """Make a :class:`RESTClient` instance from infos in an env var structured like
        "hostname:port:username:password"
        """
        features = os.environ[varname]
        return cls(*features.split(':'))

    def rest_do(self, http_verb, service_path, *args, **kwargs):
        """Generic HTTP access to the server"""
        service_url = self.base_url + service_path
        requests_func = getattr(requests, http_verb)

        # See http://docs.marklogic.com/guide/rest-dev/intro#id_34966 for ML error reporting
        rest_errors_format = {'X-Error-Accept': b'application/json'}
        if 'headers' in kwargs:
            kwargs['headers'].update(rest_errors_format)
        else:
            kwargs['headers'] = rest_errors_format
        response = requests_func(service_url, *args, auth=self.authentication, **kwargs)
        if not response.ok:
            raise MarkLogicServerError(response)
        return response
