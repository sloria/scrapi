"""
Open Science Framework harvester of public projects for the SHARE Notification Service

Example API query: https://osf.io/api/v1/search/
"""

from __future__ import unicode_literals

import json
import logging
# from dateutil.parser import parse

from nameparser import HumanName

from scrapi import requests
from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument

logger = logging.getLogger(__name__)


def process_contributors(authors):

    contributor_list = []
    for person in authors:
        name = HumanName(person)
        contributor = {
            'prefix': name.title,
            'given': name.first,
            'middle': name.middle,
            'family': name.last,
            'suffix': name.suffix,
            'email': '',
            'ORCID': '',
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


class BiomedHarvester(JSONHarvester):
    short_name = 'osf'
    long_name = 'Open Science Framework'
    url = 'http://osf.io/api/v1/search/'
    count = 0

    URL = 'http://osf.io/api/v1/search/?size=500'

    schema = {
        'title': ('title', process_null),
        'description': ('description', process_null),
        'tags': ('tags', process_tags),
        'dateUpdated': '',
        'id': {
            'serviceID': ('url', lambda x: x.replace('/', '').decode('utf-8')),
            'url': ('url', lambda x: 'http://osf.io' + x),
            'doi': 'doi'
        },
        'contributors': ('contributors', process_contributors),
        'properties': {
            'contributors_url': 'contributors_url',
            'parent_title': 'parent_title',
            'category': 'category',
            'wiki_link': 'wiki_link',
            'is_component': 'is_component',
            'is_registration': 'is_registration',
            'parent_url': 'parent_url'
        }
    }

    def harvest(self, days_back=1):
        # search_url = self.URL.format(days_back)
        search_url = self.URL
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

        total = int(records.json()['counts']['project'])
        from_arg = 0

        all_records = []
        while len(all_records) < total:
            record_list = records.json()['results']

            for record in record_list:
                if record['category'] == 'project':
                    all_records.append(record)

            from_arg += 500
            records = requests.get(search_url + '&from={}'.format(str(from_arg)), throttle=10)

        return all_records