# -*- coding: utf-8 -*-
"""
===========
mllib.utils
===========

Misc inner utilities
"""

from __future__ import unicode_literals, print_function, absolute_import

import collections
import mimetypes
import re
from urlparse import urlparse

import enum
from requests.structures import CaseInsensitiveDict

from .config import HAVE_PYTHON3, UNKNOWN_MIMETYPE, STREAM_LINE_MAX_SIZE

if HAVE_PYTHON3:
    def is_string(obj):
        return isinstance(obj, str)
else:
    def is_string(obj):
        return isinstance(obj, basestring)


def dict_pop(mapping, *keys):
    """Returns a new mapping with keys + values taken from original mapping.
     Keys are removed from original mapping

    :param mapping: original mapping
    :param keys: Keys to take to new dict and remove from original ``mapping``.
    :return: new dict with keys from ``keys`` when they exist

    .. code:: pycon

       >>> orig = {'a': 1, 'b': 2, 'c': 3}
       >>> dict_pop(orig, 'a', 'b', 'z')
       {u'a': 1, u'b': 2}
       >>> orig
       {u'c': 3}
       >>> dict_pop(orig)
       {}
       >>> orig
       {u'c': 3}
    """
    return {k: mapping.pop(k) for k in keys if k in mapping}


def is_sequence(obj):
    """Determining a Pythonic ordered sequence of objects
    """
    return isinstance(obj, (list, tuple))


def guess_mimetype(filename):
    """The mimetype of a file name or path, 'application/octet-stream' if unknown

    .. code:: pycon

       >>> guess_mimetype('foo.json')
       u'application/json'
    """
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
                for subname, subvalue in value.iteritems():
                    new_key = "{0}:{1}".format(name, subname)
                    if new_key in params:
                        params[new_key].append(subvalue)
                    else:
                        params[new_key] = [subvalue]
                del params[name]
        return params, ignored


# Validators for unique value

ident_rx = re.compile(r"^[_A-Za-z]\w*$")
filename_rx = re.compile(r"^([_\w](\w|\-)*)(\.(\w*))?$")


def is_identifier(obj):
    if not is_string(obj):
        return False
    return ident_rx.match(obj) is not None


def is_path(obj):
    if not is_string(obj):
        return False
    parts = obj.split('/')
    for part in parts[:-1]:
        if len(part) != 0 and ident_rx.match(part) is None:
            return False
    return filename_rx.match(parts[-1]) is not None


def is_fn_uri(obj):
    if not is_string(obj):
        return False
    try:
        parsed = urlparse(obj)
    except SyntaxError:
        return False
    return parsed.path is not None


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

    [('one', 'two'), ('three', 'four'), ...]


    .. code:: pycon

       >>> itt = is_2_tuple_sequence()
       >>> itt(None)
       False
       >>> itt([])
       True
       >>> itt([1])
       False
       >>> itt([('two', 'three')])
       True
       >>> itt([('two', 'three'), ('one', 'ten')])
       True
    """

    def __init__(self, allowed_keys=None, allowed_values=None):
        """Initializer

        :param allowed_keys: Allowed objects for first values in each tuple. A (frozen)set of data or callback
        :param allowed_values: Allowed objects for second values in each tuple.  A (frozen)set of data or callback
        """
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
                    return bool(controller(items[i]))
                elif isinstance(controller, frozenset):
                    if items[i] not in controller:
                        return False
                else:
                    if not is_string(items[i]):
                        return False
        return True


class is_mapping(object):
    """Validates we have a mapping (dict) with constraints

    .. code:: pycon

       >>> ctrl = is_mapping()
       >>> ctrl({})
       True
       >>> ctrl({'a':'anything'})
       True

    """

    def __init__(self, allowed_keys=None, allowed_values=None):
        """Initializer

        :param allowed_keys: Allowed objects for first values in each tuple. A (frozen)set of data or callback
        :param allowed_values: Allowed objects for second values in each tuple.  A (frozen)set of data or callback
        """
        if callable(allowed_keys) or allowed_keys is None:
            self.allowed_keys = allowed_keys
        else:
            self.allowed_keys = frozenset(allowed_keys)

        if callable(allowed_values) or allowed_values is None:
            self.allowed_values = allowed_values
        else:
            self.allowed_values = frozenset(allowed_values)

    def __call__(self, obj):
        if not isinstance(obj, collections.Mapping):
            return False

        # Validating keys
        for key in obj:
            if not is_string(key):
                return False
            if callable(self.allowed_keys):
                if not self.allowed_keys(key):
                    return False
            elif self.allowed_keys is not None:
                if key not in self.allowed_keys:
                    return False
            else:
                if not is_string(key):
                    return False

        for value in obj.itervalues():
            if callable(self.allowed_values):
                if not self.allowed_values(value):
                    return False
            elif self.allowed_values is not None:
                if value not in self.allowed_values:
                    return False
        return True

unit_validators = {
    # {keyword: callable(obj)->bool, ...}
    'uri': is_fn_uri,
    'category': lambda cat: cat in ('content', 'metadata', 'collections', 'permissions', 'properties', 'quality'),
    'database': is_identifier,
    'forest-name': is_identifier,
    'format': lambda fmt: fmt in ('xml', 'json'),
    'collection': is_identifier,
    'quality': is_positive_or_zero_int,
    'perm': is_mapping(allowed_values=('read', 'update', 'execute')),
    'prop': is_mapping(),
    'extract': lambda from_: from_ in ('properties', 'document'),
    'repair': lambda mode: mode in ('full', 'none'),
    'transform': is_identifier,
    'trans': is_mapping(),
    'temporal-collection': is_identifier,
    'vars': is_mapping(allowed_values=lambda x: True),
    'system_time': is_datetime,
    'txid': is_string,
    'xquery': is_string,
    'javascript': is_string,
    'name': is_string,
    'timeLimit': is_positive_or_zero_int
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
        (u'text', u'html', u'', {u'charset': u'utf-8'})
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
        """
        :param response: is a :class:`requests.Response` object. Associated request must have the ``streamm`` option.
        """
        self.response = response
        ct = response.headers.get('content-type', UNKNOWN_MIMETYPE)
        self.maintype, self.subtype, self.extra_type, self.ct_options = parse_mimetype(ct)
        self.boundary = bytes(self.ct_options['boundary']) if 'boundary' in self.ct_options else None

    def is_multipart_mixed(self):
        return (self.maintype, self.subtype) == ('multipart', 'mixed')

    def iter_parts(self):
        """Yields tuples of (headers, body) for each part of the response
        """
        # WTF, we do not always have a Content-Length response header. Why ?
        headers = self.response.headers
        if 'content-length' in headers and int(headers['content-length']) == 0:
            raise StopIteration

        part_start_marker = b'--' + self.boundary
        parts_end_marker = b'--' + self.boundary + b'--'
        states = enum.Enum('states', ('BOUNDARY', 'HEADERS', 'BODY'))
        state = states.BOUNDARY
        for line in self.response.iter_lines(chunk_size=STREAM_LINE_MAX_SIZE):
            if state == states.BOUNDARY:
                # Waiting for headers
                if line.strip() == part_start_marker:
                    state = states.HEADERS
                    headers = CaseInsensitiveDict()

            elif state == states.HEADERS:
                line = line.strip()
                if line == '':
                    state = states.BODY
                    chunks = []
                else:
                    name, value = line.split(':', 1)
                    headers[name.strip()] = value.strip()

            elif state == states.BODY:
                if line.strip() == part_start_marker:
                    yield headers, b''.join(chunks).strip()  # Lines have their \n terminator
                    state = states.HEADERS
                    headers = CaseInsensitiveDict()
                    chunks = []
                elif line.strip() == parts_end_marker:
                    yield headers, b''.join(chunks).strip()  # Lines have their \n terminator
                    raise StopIteration
                else:
                    chunks.append(line)
