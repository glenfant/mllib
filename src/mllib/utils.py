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

import enum
from requests.structures import CaseInsensitiveDict

from .config import HAVE_PYTHON3, UNKNOWN_MIMETYPE

if HAVE_PYTHON3:
    def is_string(obj):
            return isinstance(obj, str)
else:
    def is_string(obj):
        return isinstance(obj, basestring)


def is_sequence(obj):
    return isinstance(obj, (list, tuple))


def guess_mimetype(filename):
    """The mimetype of a file name or path, 'application/octet-stream' if unknown"""
    mt, _ = mimetypes.guess_type(filename)
    if mt is None:
        return UNKNOWN_MIMETYPE
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

            # Special effect for 'perm', 'prop' and 'trans' parameters
            if name in ('perm', 'prop', 'trans'):
                for subname, subvalue in value:
                    new_key = "{0}:{1}".format(name, subname)
                    if new_key in params:
                        params[new_key].append(subvalue)
                    else:
                        params[new_key] = [subvalue]
                del params[name]
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
    if obj == UNKNOWN_MIMETYPE:
        return True
    return mimetypes.guess_extension(obj) is not None


def is_positive_or_zero_int(obj):
    try:
        obj = int(obj)
    except ValueError:
        return False
    return obj >= 0


def is_ncname(obj):
    if not is_identifier(obj):
        return False
    return obj.find(':') == -1


def is_datetime(obj):
    # TODO: a real func
    return True


class is_2_tuple_sequence(object):
    """Validates we have a sequence of tuples like

    [('one', 'two'), ('three', four), ...]
    """
    def __init__(self, allowed_keys=None, allowed_values=None):
        if callable(allowed_keys) or allowed_keys is None:
            self.allowed_keys = allowed_keys
        else:
            self.allowed_keys = frozenset(allowed_keys)

        if callable(allowed_values) or allowed_values is None:
            self.allowed_values = allowed_values
        else:
            self.allowed_values = frozenset(allowed_values)

    def __call__(self, obj):
        if not isinstance(obj, (tuple, list)):
            return False
        for items in obj:
            if not isinstance(items, (tuple, list)):
                return False
            if len(items) != 2:
                return False

            for i, controller in enumerate((self.allowed_keys, self.allowed_values)):
                if callable(controller):
                    if not controller(items[i]):
                        return False
                elif isinstance(controller, frozenset):
                    if items[i] not in controller:
                        return False
                else:
                    if not is_string(items[i]):
                        return False
        return True


unit_validators = {
    # {keyword: callable(obj)->bool, ...}
    'uri': is_path,
    'category': lambda cat: cat in ('content', 'metadata', 'collections', 'permissions', 'properties', 'quality'),
    'database': is_identifier,
    'forest-name': is_identifier,
    'format': lambda fmt: fmt in ('xml', 'json'),
    'collection': is_identifier,
    'quality': is_positive_or_zero_int,
    'perm': is_2_tuple_sequence(allowed_values=('read', 'update', 'execute')),
    'prop': is_2_tuple_sequence(),
    'extract': lambda from_: from_ in ('properties', 'document'),
    'repair': lambda mode: mode in ('full', 'none'),
    'transform': is_identifier,
    'trans': is_2_tuple_sequence(),
    'temporal-collection': is_identifier,
    'system_time': is_datetime,
}


def multipart_response_iter(response):
    pass


def parse_mimetype(mimetype):
    """Parses a MIME type into its components.
    Stolen from aiohttp
    :param str mimetype: MIME type
    :returns: 4 element tuple for MIME type, subtype, suffix and parameters
    :rtype: tuple
    Example:

        >>> parse_mimetype('text/html; charset=utf-8')
        ('text', 'html', '', {'charset': 'utf-8'})
    """
    if not mimetype:
        return '', '', '', {}

    parts = mimetype.split(';')
    params = []
    for item in parts[1:]:
        if not item:
            continue
        key, value = item.split('=', 1) if '=' in item else (item, '')
        params.append((key.lower().strip(), value.strip(' "')))
    params = dict(params)

    fulltype = parts[0].strip().lower()
    if fulltype == '*':
        fulltype = '*/*'

    mtype, stype = fulltype.split('/', 1) if '/' in fulltype else (fulltype, '')
    stype, suffix = stype.split('+', 1) if '+' in stype else (stype, '')

    return mtype, stype, suffix, params


class ResponseAdapter(object):
    """An application oriented helper for requests.Response handling
    """
    def __init__(self, response):
        if False:
            # Pycharme helper
            import requests
            self.response = requests.Response()
        self.response = response
        ct = response.headers.get('content-type', UNKNOWN_MIMETYPE)
        self.maintype, self.subtype, self.extra_type, self.ct_options = parse_mimetype(ct)
        self.boundary = bytes(self.ct_options['boundary']) if 'boundary' in self.ct_options else None

    def is_multipart_mixed(self):
        return (self.maintype, self.subtype) == ('multipart', 'mixed')

    def iter_parts(self):
        """Yields tuples of (headers, body) for each part of the response
        """
        part_start_marker = b'--' + self.boundary
        parts_end_marker = b'--' + self.boundary + b'--'
        states = enum.Enum('states', ('BOUNDARY', 'HEADERS', 'BODY'))
        state = states.BOUNDARY
        for line in self.response.iter_lines():
            if state == states.BOUNDARY:
                # Waiting for headers
                if line.strip() == part_start_marker:
                    state = states.HEADERS
                    headers = CaseInsensitiveDict()

            elif state == states.HEADERS:
                line = line.strip()
                if line == '':
                    state = states.BODY
                    chunk = []
                else:
                    name, value = line.split(':', 1)
                    headers[name.strip()] = value.strip()

            elif state == states.BODY:
                if line.strip() == part_start_marker:
                    yield headers, b'\n'.join(chunk)
                    state = states.BOUNDARY
                elif line.strip() == parts_end_marker:
                    yield headers, b'\n'.join(chunk)
                    raise StopIteration
                else:
                    chunk.append(line)
