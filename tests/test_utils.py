# -*- coding: utf-8 -*-
"""
===================
Testing mllib.utils
===================
"""
from __future__ import unicode_literals, print_function, absolute_import

import unittest

import requests

import mllib.utils
import mllib.config


class IsStringTest(unittest.TestCase):
    """Checking object being son kind of string"""

    def test_string(self):
        """Test from a bytes string"""
        self.assertTrue(mllib.utils.is_string(b'yeah'))

    def test_unicode(self):
        """Test from unicode string"""
        self.assertTrue(mllib.utils.is_string('yeah'))

    def test_anything(self):
        """Test from anything else"""
        self.assertFalse(mllib.utils.is_string(10))


class GuessMimetypeTest(unittest.TestCase):
    """Guess mime type of a file"""

    def test_unknown(self):
        """Unknown mimetype"""
        self.assertEqual(mllib.utils.guess_mimetype('foo.unknown'), mllib.config.UNKNOWN_MIMETYPE)

    def test_xml(self):
        """An XML file"""
        self.assertEqual(mllib.utils.guess_mimetype('foo.xml'), 'application/xml')

    def test_xquery(self):
        """An XQuery file - added by mllib"""
        self.assertEqual(mllib.utils.guess_mimetype('foo.xqy'), 'application/xquery')


class KwargsSerializerTest(unittest.TestCase):
    def test_zero_or_one(self):
        """Zero or one parameter: '?'"""
        all_keywords = {'database': '?'}
        serializer = mllib.utils.KwargsSerializer(all_keywords)

        # One
        kwargs = {'database': 'schtroumpf', 'ignored': 'dummy'}
        params, ignored = serializer.request_params(kwargs)

        self.assertDictEqual(ignored, {'ignored': 'dummy'})
        self.assertEqual(params['database'], 'schtroumpf')

        # Zero
        kwargs = {'ignored': 'dummy'}
        params, ignored = serializer.request_params(kwargs)
        self.assertDictEqual(params, {})

        # More (not allowed)
        kwargs = {'database': ['one', 'two', 'three']}
        with self.assertRaises(ValueError):
            params, ignored = serializer.request_params(kwargs)

    def test_any(self):
        """Any number of arguments: '*'"""
        all_keywords = {'uri': '*'}
        serializer = mllib.utils.KwargsSerializer(all_keywords)

        # Zero arg
        kwargs = {}
        params, ignored = serializer.request_params(kwargs)
        self.assertDictEqual(params, {})

        # Only one arg
        kwargs = {'uri': 'foo'}
        params, ignored = serializer.request_params(kwargs)
        self.assertDictEqual(params, {'uri': 'foo'})

        # Two args or more
        kwargs = {'uri': ['one', 'two', 'three']}
        params, ignored = serializer.request_params(kwargs)
        self.assertDictEqual(params, {'uri': ('one', 'two', 'three')})

    def test_only_one(self):
        """Exactly one argument: '!'"""
        all_keywords = {'uri': '!'}
        serializer = mllib.utils.KwargsSerializer(all_keywords)

        # Zero
        with self.assertRaises(ValueError):
            params, ignored = serializer.request_params({})

        # One
        params, ignored = serializer.request_params({'uri': 'foo'})
        self.assertDictEqual(params, {'uri': 'foo'})

        # More than One
        with self.assertRaises(ValueError):
            params, ignored = serializer.request_params({'uri': ['one', 'two', 'three']})

    def test_one_or_more(self):
        """One or more arguments: '+'"""
        all_keywords = {'uri': '+'}
        serializer = mllib.utils.KwargsSerializer(all_keywords)

        # Zero
        with self.assertRaises(ValueError):
            params, ignored = serializer.request_params({})

        # One
        params, ignored = serializer.request_params({'uri': 'foo'})
        self.assertDictEqual(params, {'uri': 'foo'})

        # Two or more
        kwargs = {'uri': ['one', 'two', 'three']}
        params, ignored = serializer.request_params(kwargs)
        self.assertDictEqual(params, {'uri': ('one', 'two', 'three')})

    def test_rest_formatting(self):
        """Correctness of formatting for a HTTP query"""
        self.maxDiff = None
        all_keywords = {
            'uri': '+',
            'category': '*',
            'database': '*',
            'format': '*',
            'collection': '*',
            'quality': '?',
            'perm': '?',
            'prop': '?'
        }
        serializer = mllib.utils.KwargsSerializer(all_keywords)

        query_data = {
            'uri': ['aaa/bbb.xml', 'ccc/ddd.json'],
            'category': 'metadata',
            'database': 'blahblah',
            'collection': ['one', 'two'],
            'quality': '3',
            'perm': [('rest-writer', 'update')],
            'prop': [('intensity', 'good')]
        }
        params, ignored = serializer.request_params(query_data)

        # Note that some methods supported by requests and MarkLogic are not supported by httpbin.org
        expected = query_data.copy()
        del expected['perm']
        del expected['prop']
        expected['perm:rest-writer'] = 'update'
        expected['prop:intensity'] = 'good'

        for method, uri in (
                (requests.get, 'http://httpbin.org/get'),
                (requests.post, 'http://httpbin.org/post'),
                (requests.put, 'http://httpbin.org/put'),
                (requests.patch, 'http://httpbin.org/patch'),
                (requests.delete, 'http://httpbin.org/delete')):
            response = method(uri, params=params)
            self.assertTrue(response.ok)
            self.assertDictEqual(response.json()['args'], expected)


class ValidatorsTest(unittest.TestCase):
    """Validators for unique value"""

    def test_is_identifier(self):
        is_id = mllib.utils.is_identifier
        self.assertTrue(is_id('fooBar_0'))
        self.assertFalse(is_id('123acc'))
        self.assertFalse(is_id(4321))

    def test_is_path(self):
        is_path = mllib.utils.is_path
        self.assertTrue(is_path('foo'))
        self.assertTrue(is_path('foo.bar'))
        self.assertTrue(is_path('foo/bar.baz'))
        self.assertFalse(is_path('/foo/bar.baz'))
        self.assertFalse(is_path('foo.x/bar.baz'))

    def test_is_mimetype(self):
        is_mt = mllib.utils.is_mimetype
        self.assertTrue(is_mt('text/plain'))
        self.assertTrue(is_mt('application/xquery'))
        self.assertFalse(is_mt('anything/else'))

    def test_is_positive_or_zero(self):
        is_poz = mllib.utils.is_positive_or_zero_int
        self.assertTrue(is_poz(6))
        self.assertTrue(is_poz('10'))
        self.assertFalse(is_poz(-1))
        self.assertFalse(is_poz('foo'))

    def test_is_2_tuple_sequence(self):
        is_2ts = mllib.utils.is_2_tuple_sequence

        # Some invalid data
        data = {}
        validator = is_2ts()
        self.assertFalse(validator(data))

        # Three items in inner tuple when exactly two are required
        data = [('one', 'two', 'three')]
        self.assertFalse(validator(data))

        # One item in inner tuple when exactly two are required
        data = [('one',)]
        self.assertFalse(validator(data))

        # Exactly two items in inner tuples
        data = [('key', 'value'), ('key', 'value')]
        self.assertTrue(validator(data))

        # First item of inner tuple is not a str (like)
        data = [('key', 'value'), (100, 'value')]
        self.assertFalse(validator(data))

        # Constrained first values by enum
        validator = is_2ts(allowed_keys=('one', 'two'))
        data = [('one', 'schtroumpf')]
        self.assertTrue(validator(data))
        data = [('schtroumpf', 'anything')]
        self.assertFalse(validator(data))

        # Constrained second values by enum
        validator = is_2ts(allowed_values=('one', 'two'))
        data = [('schtroumpf', 'one')]
        self.assertTrue(validator(data))
        data = [('anything', 'three')]
        self.assertFalse(validator(data))

        # Constrained first value with a callback
        def is_valid(value):
            return value != 'invalid'

        validator = is_2ts(allowed_keys=is_valid)
        data = [('valid', 'one')]
        self.assertTrue(validator(data))
        data = [('invalid', 'one')]
        self.assertFalse(validator(data))

        # Constrained second value with callback
        validator = is_2ts(allowed_values=is_valid)
        data = [('one', 'valid')]
        self.assertTrue(validator(data))
        data = [('one', 'invalid')]
        self.assertFalse(validator(data))


class ParseMimetypesTest(unittest.TestCase):
    def test_null_mimetype(self):
        for null_value in ('', None, []):
            self.assertEqual(mllib.utils.parse_mimetype(null_value), ('', '', '', {}))

    def test_valid_mimetypes(self):
        testcases = [
            ('TeXt/HtmL', ('text', 'html', '', {})),
            ('text/plain; charset=us-ascii', ('text', 'plain', '', {'charset': 'us-ascii'})),
            ('text/plain; charset="us-ascii"', ('text', 'plain', '', {'charset': 'us-ascii'})),
            ('application/json+hal; charset=utf-8', ('application', 'json', 'hal', {'charset': 'utf-8'}))
        ]
        for mt_value, expected in testcases:
            self.assertEqual(mllib.utils.parse_mimetype(mt_value), expected)


class FakeResponse(object):
    def __init__(self, headers, body):
        self.headers = requests.utils.CaseInsensitiveDict(headers)
        self.body = body

    def iter_lines(self):
        for line in self.body.splitlines():
            yield line + b'\n'


MULTIPART_RAW_RESPONSE = b"""
Anything may precede the real payload

--1176113105d6eaed
Content-Type: text/plain
X-Primitive: untypedAtomic

hello
--1176113105d6eaed
Content-Type: text/plain
X-Primitive: untypedAtomic

world
--1176113105d6eaed
Content-Type: text/plain
X-Primitive: untypedAtomic

héllo
world

--1176113105d6eaed--

Anything may follow the end multipart delimiter
"""


class ResponseAdapterTest(unittest.TestCase):
    def test_multipart_mixed_content_type(self):
        headers = {'content-type': 'multipart/mixed; boundary=ARBITRARY_BOUNDARY'}
        response = FakeResponse(headers, None)
        ad = mllib.utils.ResponseAdapter(response)
        self.assertEqual(ad.maintype, 'multipart')
        self.assertEqual(ad.subtype, 'mixed')
        self.assertEqual(ad.boundary, 'ARBITRARY_BOUNDARY')

    def test_ugly_content_type(self):
        headers = {'content-type': 'this is not a valid header'}
        response = FakeResponse(headers, None)
        ad = mllib.utils.ResponseAdapter(response)
        self.assertEqual(ad.maintype, 'this is not a valid header')
        self.assertEqual(ad.subtype, '')
        self.assertIsNone(ad.boundary)

    def test_iterate_chunks(self):
        headers = {'content-type': 'Content-Type: multipart/mixed; boundary=1176113105d6eaed',
                   'content-length': '100'}
        response = FakeResponse(headers, MULTIPART_RAW_RESPONSE)
        ad = mllib.utils.ResponseAdapter(response)
        count = 0
        all_headers = []
        all_chunks = []
        for headers, chunk in ad.iter_parts():
            count += 1
            self.assertEqual(len(headers), 2)
            self.assertEqual(headers['content-type'], 'text/plain')
            self.assertEqual(headers['x-primitive'], 'untypedAtomic')
            all_headers.append(headers)
            all_chunks.append(chunk)
        self.assertEqual(count, 3)
        self.assertEqual(all_chunks[0], "hello")
        self.assertEqual(all_chunks[1], "world")
        self.assertEqual(all_chunks[2], b"héllo\nworld")


