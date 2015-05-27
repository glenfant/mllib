# -*- coding: utf-8 -*-
"""
===================
Testing mllib.utils
===================
"""

import unittest

import requests

import mllib.utils


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
        self.assertEqual(mllib.utils.guess_mimetype('foo.unknown'), mllib.utils.UNKNOWN_CONTENT_TYPE)

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
            'perm': 'update',
            'prop': 'good'
        }
        params, ignored = serializer.request_params(query_data)

        # Note that some methods supported by requests and MarkLogic are not supported by httpbin.org
        for method, uri in (
            (requests.get, 'http://httpbin.org/get'),
            (requests.post, 'http://httpbin.org/get'),
            (requests.put, 'http://httpbin.org/put'),
            (requests.patch, 'http://httpbin.org/patch'),
            (requests.delete, 'http://httpbin.org/delete')):

            response = requests.get('http://httpbin.org/get', params=params)
            self.assertTrue(response.ok)
            self.assertDictEqual(response.json()['args'], query_data)


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
