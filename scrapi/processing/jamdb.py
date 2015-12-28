from __future__ import absolute_import

import copy
import logging
import hashlib
import requests

from scrapi import events
# from scrapi.linter import RawDocument, NormalizedDocument
# from scrapi.processing import DocumentTuple
from scrapi.processing.base import BaseProcessor, BaseDatabaseManager

logger = logging.getLogger(__name__)


class JamDBProcessor(BaseProcessor):
    NAME = 'jamdb'

    manager = BaseDatabaseManager()
    base_url = 'http://localhost:1212/v1/'
    namespace = 'SHARE'
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjI0NDc3Nzk5MDgsInN1YiI6InRyYWNrZWQtU0hBUkV8dXNlcnMtY2hyaXMifQ.kVvJaZcIDDIzNb5hyey_7YqsrfZurZcqMH65aRysq_4'

    @property
    def collections(self):
        return {
            'documents': '{}-data'.format(self.namespace.lower()),
            'contributors': '{}-contributor'.format(self.namespace.lower())
        }

    @property
    def cookies(self):
        return {'cookies': self.token}

    def url_for(self, type_):
        return '{}namespaces/{}/collections/{}/documents'.format(self.base_url, self.namespace, self.collections[type_])

    def format_data(self, attributes, id_):
        return {
            'data': {
                'id': id_,
                'type': 'documents',
                'attributes': attributes
            }
        }

    def get_id(self, *args):
        return hashlib.sha1(
            '|'.join(args).encode('utf-8')
        ).hexdigest()

    def upsert(self, url, data):
        response = requests.patch(url + '/{}'.format(data['data']['id']), cookies=self.cookies, json=data)
        if response.status_code == 404:
            response = requests.post(url, cookies=self.cookies, json=data)
        return response

    @events.logged(events.PROCESSING, 'raw.jamdb')
    def process_raw(self, raw_doc):
        data = self.format_data({'raw': raw_doc.attributes}, self.get_id(raw_doc['source'], raw_doc['docID']))
        self.upsert(self.url_for('documents'), data)

    @events.logged(events.PROCESSING, 'normalized.jamdb')
    def process_normalized(self, raw_doc, normalized):
        normalized = self.process_contributors(raw_doc, normalized)
        data = self.format_data({'normalized': normalized.attributes}, self.get_id(raw_doc['source'], raw_doc['docID']))
        self.upsert(self.url_for('documents'), data)

    def process_contributors(self, raw_doc, normalized):
        source, docID = raw_doc['source'], raw_doc['docID']
        normalized = copy.deepcopy(normalized)
        norm_id = self.get_id(source, docID)

        for i, contributor in enumerate(normalized['contributors']):
            contrib_id = self.get_id(source, docID, contributor['name'])
            contributor['researchObjects'] = [{'title': normalized['title'], 'id': norm_id}]
            data = self.format_data(contributor, contrib_id)
            self.upsert(self.url_for('contributors'), data)
            normalized['contributors'][i]['id'] = contrib_id
        return normalized

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
