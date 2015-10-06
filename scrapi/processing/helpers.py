from __future__ import absolute_import

import datetime
import requests


def save_status_of_uri(uri, uritype):
    uri_status = requests.get(uri)

    return {
        'actual_uri': uri,
        'uritype': uritype,
        'resolved_uri': uri_status.url,
        'resolved_datetime': datetime.datetime.now(),
        'resolved_status': uri_status.status_code,
    }
