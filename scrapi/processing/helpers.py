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


def query_orcid_api(id_email):
    orcid_email_query = 'http://pub.orcid.org/v1.2/search/orcid-bio?q=email:{}'.format(id_email)

    orcid_results = requests.get(orcid_email_query, headers={'Accept': 'application/orcid+json'}).json()
    number_results = orcid_results['orcid-search-results']['num-found']

    if number_results > 0:
        return number_results
    else:
        return None
