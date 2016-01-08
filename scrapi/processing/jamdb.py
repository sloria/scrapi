from __future__ import absolute_import

import copy
import logging
import hashlib
import requests

from scrapi import events
from scrapi import settings
from scrapi.processing.base import BaseProcessor, BaseDatabaseManager

logger = logging.getLogger(__name__)


class JamManager(BaseDatabaseManager):

    def setup(self):
        success = True
        for collection in ['research-objects', 'contributors']:
            response = requests.post(
                '{}namespaces/{}/collections/'.format(JamDBProcessor.base_url, JamDBProcessor.namespace),
                headers=JamDBProcessor.headers,
                json={
                    'data': {
                        'type': 'collections',
                        'attributes': {},
                        'id': collection
                    }
                }
            )
            success = success and response.status_code in [201, 409]
        return success


class JamDBProcessor(BaseProcessor):
    NAME = 'jamdb'

    manager = JamManager()
    # base_url = 'http://localhost:1212/v1/'
    base_url = settings.JAMDB_BASE_URL
    namespace = settings.JAMDB_NAMESPACE

    headers = {'Authorization': settings.JAMDB_TOKEN }

    @property
    def collections(self):
        return {
            'documents': 'research-objects'.format(self.namespace.lower()),
            'contributors': 'contributors'.format(self.namespace.lower())
        }

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
        response = requests.patch(url + '/{}'.format(data['data']['id']), headers=self.headers, json=data)
        if response.status_code == 404:
            response = requests.post(url, headers=self.headers, json=data)
            assert response.status_code == 201
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
