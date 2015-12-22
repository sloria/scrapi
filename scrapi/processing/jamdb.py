from __future__ import absolute_import

import logging

from scrapi import events, requests
from scrapi.linter import RawDocument, NormalizedDocument
from scrapi.processing import DocumentTuple
from scrapi.processing.base import BaseProcessor, FakeDatabaseManager

logger = logging.getLogger(__name__)


class JamDBProcessor(BaseProcessor):
    NAME = 'jamdb'

    manager = FakeDatabaseManager()

    @events.logged(events.PROCESSING, 'raw.jamdb')
    def process_raw(self, raw_doc):
        requests.post(
            '{}/namespaces/{}/collections/{}/documents'.format(
                self.base_url, self.namespace, self.collection
            ),
            cookie=self.cookie,
            json={
                'data': {
                    'id': self.get_id(raw_doc['source'], raw_doc['docID']),
                    'type': 'documents',
                    'attributes': raw_doc.attributes
                }
            }
        )

    @events.logged(events.PROCESSING, 'normalized.jamdb')
    def process_normalized(self, raw_doc, normalized):
        raise NotImplementedError

    def documents(self, *sources):
        raise NotImplementedError

    def get(self, source, docID):
        raise NotImplementedError

    def delete(self, source, docID):
        raise NotImplementedError

    def create(self, attributes):
        raise NotImplementedError

    def get_versions(self, source, docID):
        raise NotImplementedError
