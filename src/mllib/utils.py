# -*- coding: utf-8 -*-
"""
===========
mllib.utils
===========

Misc inner utilities
"""

from __future__ import unicode_literals, print_function, absolute_import

import mimetypes
import re
import sys


HAVE_PYTHON3 = sys.version_info[0] == 3

if HAVE_PYTHON3:
    def is_string(obj):
            return isinstance(obj, str)
else:
    def is_string(obj):
        return isinstance(obj, basestring)

def is_sequence(obj):
    return isinstance(obj, (list, tuple))


UNKNOWN_CONTENT_TYPE = "application/octet-stream"


def guess_mimetype(filename):
    """The mimetype of a file name or path, 'application/octet-stream' if unknown"""
    mt, _ = mimetypes.guess_type(filename)
    if mt is None:
        return UNKNOWN_CONTENT_TYPE
    return mt


class KwargsSerializer(object):
    def __init__(self, specs):
        """
        :param specs: mapping of {name: req, ...} where name is the name of a parameter, req is one of :
          - '!': Exactly on parameter required
          - '?': Optional parameter (zeo or one)
          - '*': Zero or more parameter
          - '+': One or more parameter
        """
        assert frozenset(specs.values()) <= {'!', '?', '+', '*'}
        self.specs = specs

    def request_params(self, kwargs, params=None):
        """Builds params suitable to request.get/post/...

        :param kwargs: provided named args to a REST request
        :param params: URL parameters
        :type params: dict
        """
        if params is None:
            params = {}
        ignored = {}

        # Checking required parameters
        for name, req in self.specs.iteritems():
            if req not in ('!', '+'):
                continue
            if name not in kwargs:
                raise ValueError("{0} keyword argument must be provided".format(name))

        for name, value in kwargs.iteritems():
            if name not in self.specs:
                ignored[name] = value
                continue

            value_spec = self.specs[name]

            if value_spec in ('!', '?'):
                if not unit_validators[name](value):
                    raise ValueError("Invalid value for {0}, got: {1}".format(name, value))
                params[name] = value

            elif value_spec in ('*', '+'):
                if isinstance(value, (list, tuple, dict, set, frozenset)):
                    param_values = []
                    for elem in value:
                        if not unit_validators[name](elem):
                            raise ValueError("Invalid value for {0}, got: {1}".format(name, elem))
                        param_values.append(elem)
                    if len(param_values) > 0:
                        params[name] = tuple(param_values)
                else:
                    if not unit_validators[name](value):
                        raise ValueError("Invalid value for {0}, got: {1}".format(name, value))
                    params[name] = value

            else:
                raise ValueError("Invalid count spec for {0}: {1}".format(name, value_spec))

        return params, ignored


# Validators for unique value

ident_rx = re.compile(r"^[_A-Za-z]\w*$")
filename_rx = re.compile(r"^([_A-Za-z]\w*)(\.(\w*))?$")


def is_identifier(obj):
    if not is_string(obj):
        return False
    return ident_rx.match(obj) is not None


def is_path(obj):
    if not is_string(obj):
        return False
    parts = obj.split('/')
    for part in parts[:-1]:
        if ident_rx.match(part) is None:
            return False
    return filename_rx.match(parts[-1]) is not None


def is_mimetype(obj):
    if not is_string(obj):
        return False
    if obj == UNKNOWN_CONTENT_TYPE:
        return True
    return mimetypes.guess_extension(obj) is not None


def is_positive_or_zero_int(obj):
    try:
        obj = int(obj)
    except ValueError:
        return False
    return obj >= 0


unit_validators = {
    'uri': is_path,
    'category': lambda cat: cat in ('content', 'metadata', 'collections', 'permissions', 'properties', 'quality'),
    'database': is_identifier,
    'format': lambda fmt: fmt in ('xml', 'json'),
    'collection': is_identifier,
    'quality': is_positive_or_zero_int,
    'perm': lambda perm: perm in ('read', 'update', 'execute'),
    'prop': is_identifier
}
