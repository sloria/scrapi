"""
Open Science Framework harvester of public projects for the SHARE Notification Service

Example API query: https://osf.io/api/v1/search/
https://staging.osf.io/api/v1/search/?q=category:registration%20AND%20date_created:[2015-01-01%20TO%202015-03-10]&size=1000
https://osf.io/api/v1/search/?q=category:registration%20AND%20NOT%20title=test%20AND%20NOT%20title=%22Test%20Project%22
"""

from __future__ import unicode_literals

import json
import logging
from datetime import date, timedelta

from scrapi import requests
from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument
from scrapi.base.helpers import (
    compose,
    parse_name,
    coerce_to_list,
    build_properties,
    datetime_formatter
)

logger = logging.getLogger(__name__)

url_from_guid = 'https://osf.io{}'.format


def process_contributors(authors):

    contributor_list = []
    for person in authors:
        contributor = parse_name(person['fullname'])
        contributor['sameAs'] = [url_from_guid(person['url'])]
        contributor_list.append(contributor)

    return contributor_list


class OSFHarvester(JSONHarvester):
    short_name = 'osf'
    long_name = 'Open Science Framework'
    url = 'http://osf.io/api/v1/search/'
    count = 0

    # Only registrations that aren't just the word "test" or "test project"
    URL = 'https://osf.io/api/v1/search/?q=category:registration ' +\
          ' AND registered_date:[{} TO {}]' +\
          ' AND NOT title=test AND NOT title="Test Project"&size=1000'

    @property
    def schema(self):
        return {
            'contributors': ('/contributors', process_contributors),
            'title': ('/title', lambda x: x or ''),
            'providerUpdatedDateTime': ('/date_registered', datetime_formatter),
            'description': '/description',
            'uris': {
                'canonicalUri': ('/url', url_from_guid),
                'providerUris': ('/url', compose(coerce_to_list, url_from_guid))
            },
            'tags': '/tags',
            'otherProperties': build_properties(
                ('parent_title', '/parent_title'),
                ('category', '/category'),
                ('wiki_link', '/wiki_link'),
                ('is_component', '/is_component'),
                ('is_registration', '/is_registration'),
                ('parent_url', '/parent_url'),
                ('journal Id', '/journal Id')
            )
        }

    def harvest(self, start_date=None, end_date=None, page_limit=None):
        # Always harvest a 2 day period starting 2 days back to honor time given
        # to contributors to cancel a public registration
        start_date = start_date or date.today() - timedelta(4)
        end_date = end_date or date.today() - timedelta(2)

        search_url = self.URL.format(start_date.isoformat(), end_date.isoformat())
        records = self.get_records(search_url, page_limit)

        record_list = []
        for record in records:
            doc_id = record['url'].replace('/', '')

            record_list.append(
                RawDocument(
                    {
                        'doc': json.dumps(record),
                        'source': self.short_name,
                        'docID': doc_id,
                        'filetype': 'json'
                    }
                )
            )

        return record_list

    def get_records(self, search_url, page_limit):
        records = requests.get(search_url)

        total = int(records.json()['counts']['registration'])

        from_arg = 0
        all_records = []
        while len(all_records) < total:
            record_list = records.json()['results']

            for record in record_list:
                all_records.append(record)

            from_arg += 1000

            if page_limit and int(page_limit) == from_arg / 1000:
                break
            else:
                records = requests.get(search_url + '&from={}'.format(str(from_arg)), throttle=10)

        return all_records
