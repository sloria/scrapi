from __future__ import absolute_import

import os
import datetime
import requests
import logging

from scrapi.processing.base import BaseProcessor

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")
from api.webview.models import Document


logger = logging.getLogger(__name__)


class UriProcessor(BaseProcessor):
    NAME = 'uri_logging'

    def process_uris(self, source, docID, uri, uritype, **kwargs):
        try:
            document = Document.objects.get(source=source, docID=docID)
            processed_normalized = self.save_status_of_uri(document.normalized, uri, uritype)

            document.normalized = processed_normalized

            document.save()
        except TypeError:
            pass

    def save_status_of_uri(self, normalized, uri, uritype):
        uri_status = requests.get(uri)

        status = {
            'actual_uri': uri,
            'uritype': uritype,
            'resolved_uri': uri_status.url,
            'resolved_datetime': datetime.datetime.now(),
            'resolved_status': uri_status.status_code,
            'is_doi': True if 'dx.doi.org' in normalized['uris']['canonicalUri'] else False
        }

        try:
            normalized['shareProperties']['uri_logs']['status'].append(status)
        except KeyError:
            normalized['shareProperties']['uri_logs'] = {}
            normalized['shareProperties']['uri_logs']['status'] = [status]

        return normalized
