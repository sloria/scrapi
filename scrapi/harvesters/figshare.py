"""
Figshare harvester of public projects for the SHARE Notification Service
Note: At the moment, this harvester only harvests basic data on each article, and does
not make a seperate request for additional metadata for each record.

Example API query: http://api.figshare.com/v1/articles/search?search_for=*&from_date=2015-2-1&to_date=2015-2-1
"""

from __future__ import unicode_literals

import json
import logging
from dateutil.parser import parse
from datetime import date, timedelta, datetime


from scrapi import requests
from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument
from scrapi.base.helpers import default_name_parser, build_properties

logger = logging.getLogger(__name__)


class FigshareHarvester(JSONHarvester):
    short_name = 'figshare'
    long_name = 'figshare'
    url = 'http://figshare.com/'

    URL = 'http://api.figshare.com/v1/articles/search?search_for=*&from_date='

    schema = {
        'title': '/title',
        'description': '/description',
        'contributors': ('/authors', lambda x: default_name_parser([person['author_name'] for person in x])),
        'providerUpdatedDateTime': ('/modified_date', lambda x: parse(x).date().isoformat().decode('utf-8')),
        'uris': {
            'canonicalUri': ('/DOI', lambda x: x[0] if isinstance(x, list) else x),
            'providerUris': [
                ('/url')
            ]
        },
        'otherProperties': build_properties(
            ('serviceID', ('/article_id', lambda x: str(x).decode('utf-8'))),
            ('definedType', '/defined_type'),
            ('type', '/type'),
            ('links', '/links'),
            ('publishedDate', '/published_date')
        )
    }

    def harvest(self, start_date=None, end_date=None):
        """ Figshare should always have a 24 hour delay because they
        manually go through and check for test projects. Most of them
        are removed within 24 hours.
        """
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() - timedelta(1) if start_date else date.today().isoformat()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() - timedelta(1) if end_date else (date.today() - timedelta(1)).isoformat()

        search_url = '{0}{1}&to_date={2}'.format(
            self.URL,
            start_date,
            end_date
        )

        records = self.get_records(search_url)

        record_list = []
        for record in records:
            doc_id = record['article_id']

            record_list.append(
                RawDocument(
                    {
                        'doc': json.dumps(record),
                        'source': self.short_name,
                        'docID': unicode(doc_id),
                        'filetype': 'json'
                    }
                )
            )

        return record_list

    def get_records(self, search_url):
        records = requests.get(search_url)
        total_records = records.json()['items_found']
        page = 1

        all_records = []
        while len(all_records) < total_records:
            record_list = records.json()['items']

            for record in record_list:
                if len(all_records) < total_records:
                    all_records.append(record)

            page += 1
            records = requests.get(search_url + '&page={}'.format(str(page)), throttle=3)

        return all_records
