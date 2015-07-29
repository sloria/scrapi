from __future__ import absolute_import

import os
import json
import datetime
import requests

import copy
import logging

from scrapi import events
from scrapi.processing.base import BaseProcessor

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")
from django.core.exceptions import ObjectDoesNotExist
from api.webview.models import Document

logger = logging.getLogger(__name__)


class PostgresProcessor(BaseProcessor):
    NAME = 'postgres'

    @events.logged(events.PROCESSING, 'raw.postgres')
    def process_raw(self, raw_doc):
        source, docID = raw_doc['source'], raw_doc['docID']
        document = self._get_by_source_id(Document, source, docID) or Document(source=source, docID=docID)

        modified_doc = copy.deepcopy(raw_doc.attributes)
        if modified_doc.get('versions'):
            modified_doc['versions'] = str(modified_doc['versions'])

        document.raw = modified_doc

        document.save()

    @events.logged(events.PROCESSING, 'normalized.postgres')
    def process_normalized(self, raw_doc, normalized):
        source, docID = raw_doc['source'], raw_doc['docID']
        document = self._get_by_source_id(Document, source, docID) or Document(source=source, docID=docID)

        document.normalized = normalized.attributes
        document.providerUpdatedDateTime = normalized['providerUpdatedDateTime']

        document.save()

    def _get_by_source_id(self, model, source, docID):
        try:
            return Document.objects.filter(source=source, docID=docID)[0]
        except IndexError:
            return None


class UriProcessor(BaseProcessor):
    NAME = 'postgres_uri'

    def process_raw(self, raw_doc):
        pass

    def process_normalized(self, raw_doc, normalized):
        try:
            document = Document.objects.get(source=raw_doc['source'], docID=raw_doc['docID'])
            normalized_document = json.loads(document.normalized.attributes)

            processed_normalized = self.save_status_of_canonical_uri(normalized_document)
            processed_normalized = self.save_status_of_object_uris(processed_normalized)

            document.normalized = processed_normalized

            document.save()
        except ObjectDoesNotExist:
            pass

    def save_status_of_canonical_uri(self, normalized):
        cannonical_uri_status = requests.get(normalized['uris']['canonicalUri'])

        cannonical_status = {
            'resolved_uri': cannonical_uri_status.url,
            'resolved_datetime': datetime.datetime.now(),
            'resolved_status': cannonical_uri_status.status_code,
            'is_doi': True if 'dx.doi.org' in normalized['uris']['canonicalUri'] else False
        }

        try:
            normalized['shareProperties']['uri_logs']['cannonical_status'].append(cannonical_status)
        except KeyError:
            normalized['shareProperties']['uri_logs']['cannonical_status'] = [cannonical_status]

        return normalized

    def save_status_of_object_uris(self, normalized):
        all_object_uris = normalized['uris']['object_uris']

        for uri in all_object_uris:
            current_list = []
            uri_resolved = requests.get(uri)

            uri_status = {
                'resolved_uri': uri_resolved.url,
                'resolved_datetime': datetime.datetime.now(),
                'resolved_status': uri_resolved.status_code,
                'is_doi': True if 'dx.doi.org' in uri else False
            }
            current_list.append(uri_status)

        try:
            normalized['shareProperties']['uri_logs']['object_status'].append(current_list)
        except KeyError:
            normalized['shareProperties']['uri_logs']['object_status'] = [current_list]
