"""
Open Science Framework harvester of public projects for the SHARE Notification Service

Example API query: https://osf.io/api/v1/search/
https://staging.osf.io/api/v1/search/?q=category:registration%20AND%20date_created:[2015-01-01%20TO%202015-03-10]&size=1000
https://osf.io/api/v1/search/?q=category:registration%20AND%20NOT%20title=test%20AND%20NOT%20title=%22Test%20Project%22
"""

from __future__ import unicode_literals

import json
import logging
from dateutil.parser import parse
from datetime import date, timedelta

from nameparser import HumanName

from scrapi import requests
from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument
from scrapi.base.helpers import build_properties

logger = logging.getLogger(__name__)


def process_contributors(authors):

    contributor_list = []
    for person in authors:
        name = HumanName(person['fullname'])
        contributor = {
            'name': person['fullname'],
            'givenName': name.first,
            'additionalName': name.middle,
            'familyName': name.last,
            'email': '',
            'sameAs': [],
        }
        contributor_list.append(contributor)

    return contributor_list


def process_null(entry):
    if entry is None:
        return ''
    else:
        return entry


def process_tags(entry):
    if isinstance(entry, list):
        return entry
    else:
        return [entry]


def parse_date(entry):
    return parse(entry).date().isoformat().decode('utf-8')


class OSFHarvester(JSONHarvester):
    short_name = 'osf'
    long_name = 'Open Science Framework'
    url = 'http://osf.io/api/v1/search/'
    count = 0

    # Only registrations that aren't just the word "test" or "test project"
    URL = 'https://osf.io/api/v1/search/?q=category:registration ' +\
          ' AND date_created:[{} TO {}]' +\
          ' AND NOT title=test AND NOT title="Test Project"&size=1000'

    @property
    def schema(self):
        return {
            'contributors': ('/contributors', process_contributors),
            'title': ('/title', process_null),
            'providerUpdatedDateTime': ('date_created', parse_date),
            'description': ('/description', process_null),
            'uris': {
                'canonicalUri': ('/url', lambda x: 'http://osf.io' + x),
            },
            'tags': ('tags', process_tags),
            'otherProperties': build_properties(
                ('parent_title', 'parent_title'),
                ('category', 'category'),
                ('wiki_link', 'wiki_link'),
                ('is_component', 'is_component'),
                ('is_registration', 'is_registration'),
                ('parent_url', 'parent_url'),
                ('contributors', 'contributors'),
                ('journal Id', '/journal Id'),
                ('tags', ('tags', process_tags))
            )
        }

    def harvest(self, days_back=1):
        start_date = str(date.today() - timedelta(int(days_back)))
        end_date = str(date.today())

        search_url = self.URL.format(start_date, end_date)
        records = self.get_records(search_url)

        record_list = []
        for record in records:
            doc_id = record['url'].replace('/', '')

            record_list.append(
                RawDocument(
                    {
                        'doc': json.dumps(record),
                        'source': self.short_name,
                        'docID': doc_id.decode('utf-8'),
                        'filetype': 'json'
                    }
                )
            )

        return record_list

    def get_records(self, search_url):
        records = requests.get(search_url)

        try:
            total = int(records.json()['counts']['registration'])
        except KeyError:
            return []

        from_arg = 0
        all_records = []
        while len(all_records) < total:
            record_list = records.json()['results']

            for record in record_list:
                all_records.append(record)

            from_arg += 1000
            records = requests.get(search_url + '&from={}'.format(str(from_arg)), throttle=10)

        return all_records
