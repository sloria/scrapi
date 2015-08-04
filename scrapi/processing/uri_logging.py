from __future__ import absolute_import

import datetime
import requests
import logging

from scrapi.processing.base import BaseProcessor


logger = logging.getLogger(__name__)


class UriProcessor(BaseProcessor):
    NAME = 'uri_logging'

    def process_uris(self, document):
        try:
            processed_normalized = self.save_status_of_canonical_uri(document.normalized)
            processed_normalized = self.save_status_of_object_uris(processed_normalized)

            document.normalized = processed_normalized

            document.save()
        except TypeError:
            pass

    def save_status_of_canonical_uri(self, normalized):
        cannonical_uri_status = requests.get(normalized['uris']['canonicalUri'])

        cannonical_status = {
            'actual_uri': normalized['uris']['canonicalUri'],
            'resolved_uri': cannonical_uri_status.url,
            'resolved_datetime': datetime.datetime.now(),
            'resolved_status': cannonical_uri_status.status_code,
            'is_doi': True if 'dx.doi.org' in normalized['uris']['canonicalUri'] else False
        }

        try:
            normalized['shareProperties']['uri_logs']['cannonical_status'].append(cannonical_status)
        except KeyError:
            normalized['shareProperties']['uri_logs'] = {}
            normalized['shareProperties']['uri_logs']['cannonical_status'] = [cannonical_status]

        return normalized

    def save_status_of_object_uris(self, normalized):
        try:
            all_object_uris = normalized['uris']['object_uris']
        except KeyError:
            return normalized

        for uri in all_object_uris:
            current_list = []
            uri_resolved = requests.get(uri)

            uri_status = {
                'actual_uri': uri,
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

        return normalized
