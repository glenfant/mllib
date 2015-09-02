# -*- coding: utf-8 -*-
"""
===============
mllib.documents
===============

http://docs.marklogic.com/guide/rest-dev/documents
http://docs.marklogic.com/REST/client/management
"""

from __future__ import unicode_literals, print_function, absolute_import

from .restclient import RESTClient
from .utils import KwargsSerializer, guess_mimetype, is_sequence, ResponseAdapter
from .config import UNKNOWN_MIMETYPE


class DocumentsService(RESTClient):

    def document_put(self, file_, **kwargs):
        """Insert or update document contents and/or metadata, at a caller-supplied document URI.
        http://docs.marklogic.com/REST/PUT/v1/documents

        :param file_: A path to a file or an opened file object in 'rb' mode.
        :param kwargs: Named arguments from the dict ``requirements`` below
        :return: a :class:`requests.Response` object
        :raise: a :class:`mllib.mlexceptions.MarkLogicServerError` on bad requests
        """
        requirements = {
            'uri': '!',
            'category': '*',
            'database': '?',
            'format': '?',
            'collection': '*',
            'quality': '?',
            'perm': '*',
            'prop': '*',
            'extract': '?',
            'repair': '?',
            'transform': '?',
            'trans': '*',
            'txid': '?',
            'lang': '?',
            'forest-name': '?',
            'temporal-collection': '?',
            'system-time': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)

        if hasattr(file_, 'name'):
            ct = guess_mimetype(file_.name)
        else:
            ct = UNKNOWN_MIMETYPE
        headers = {'Content-type': ct}
        response = self.rest_put('/v1/documents', params=params, data=file_, headers=headers)
        return response

    def document_get(self, **kwargs):
        """Retrieve document content and/or metadata from the database.
        http://docs.marklogic.com/REST/GET/v1/documents

        :param kwargs: Named arguments from the dict ``requirements`` below
        :return: a :class:`requests.Response` object or a :class:`mllib.utils.ResponseAdapter` when multiple
          documents are returned
        :raise: a :class:`mllib.mlexceptions.MarkLogicServerError` on bad requests
        """
        requirements = {
            'uri': '+',
            'database': '?',
            'category': '*',
            'format': '?',
            'transform': '?',
            'trans': '*',
            'txid': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)
        category = params.get('category', [])
        if is_sequence(params['uri']) or ({'content', 'metadata'} <= frozenset(category)):
            headers = {'Accept': 'multipart/mixed'}
            response_adapter = ResponseAdapter
        else:
            headers = {}
            response_adapter = lambda x: x  # Neutral adapter
        response = self.rest_get('/v1/documents', params=params, headers=headers)
        return response_adapter(response)

    def document_delete(self, **kwargs):
        """Remove documents, or reset document metadata.
        http://docs.marklogic.com/REST/DELETE/v1/documents

        :param kwargs: Named arguments from the dict ``requirements`` below
        :return: a :class:`requests.Response` object
        """
        requirements = {
            'uri': '+',
            'category': '*',
            'database': '?',
            'txid': '?',
            'temporal-collection': '?',
            'system-time': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)
        response = self.rest_delete('/v1/documents', params=params)
        return response

    def document_patch(self, file_, **kwargs):
        """Perform a partial update to content or metadata of a document.
        http://docs.marklogic.com/REST/PATCH/v1/documents

        :param file_: The content of the patch, see http://docs.marklogic.com/guide/rest-dev/documents#id_15775
        :param kwargs: Named arguments from the dict ``requirements`` below
        :return: a :class:`requests.Response` object
        """
        requirements = {
            'uri': '!',
            'category': '*',
            'database': '?',
            'format': '?',
            'txid': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)

        if hasattr(file_, 'name'):
            ct = guess_mimetype(file_.name)
        else:
            ct = UNKNOWN_MIMETYPE
        headers = {'Content-type': ct}

        response = self.rest_patch('/v1/documents', params=params, data=file_, headers=headers)
        return response

    def document_post(self, **kwargs):
        """Insert or update content and/or metadata for multiple documents in a single request.
        http://docs.marklogic.com/REST/POST/v1/documents

        :param kwargs:
        :return:
        """
        return

