"""
dataverse.harvard harvester of public projects for the SHARE Notification Service
Note: At the moment, this harvester only harvests basic data on each article, and does
not make a seperate request for additional metadata for each record.

Example API query: https://dataverse.harvard.edu/api/search?q=title&key=$API_KEY
"""

from __future__ import unicode_literals

import json
import logging
from dateutil.parser import parse
from datetime import timedelta
import datetime

from scrapi import requests
from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument
from scrapi.base.helpers import  build_properties

logger = logging.getLogger(__name__)


def institution_name_parser(names):
    ''' Parse institution names '''
    contributor_list = []
    for inst in names:
        contributor = {
            'name': inst,
            'email': '',
            'sameAs': []
        }
        contributor_list.append(contributor)

    return contributor_list


class harvardDataverseHarvester(JSONHarvester):
    short_name = 'harvard'
    long_name = 'harvard dataverse'
    url = 'https://dataverse.harvard.edu/'

    URL = 'https://dataverse.harvard.edu/api/search?q=*&key=0b684d79-3c44-4ace-8583-dba5e0f11600'

    schema = {
        'title': '/title',
        'description': '/description',
        'contributors':  ('/authors', lambda x:institution_name_parser(x)),
        'providerUpdatedDateTime': '/published_at',
        'uris': {
           'objectUri': '/image_url',
            'providerUris': '/url'


        },
        'otherProperties': build_properties(
            ('type', '/type'),
            ('citation', '/citation'),
        )
    }

    def harvest(self, start_date=None, end_date=None):

        if start_date is None:
            start_date = datetime.datetime.now() - timedelta(2)
        if end_date is None:
            end_date = datetime.datetime.now()

        base_url = 'https://dataverse.harvard.edu/api/search?q=*&sort=date&order=desc&key=0b684d79-3c44-4ace-8583-dba5e0f11600&start={}'
        total = requests.get(base_url.format(0)).json()['data']['total_count']
        logger.info('{} documents to be harvested'.format(total))

        doc_list = []
        condition = True
        start = 0

        while(condition):
            records = requests.get(base_url.format(start)).json()['data']['items']
            for record in records:
                if  start_date < parse(record['published_at']).date() <= end_date:
                   doc_id = record['url']
                    doc_list.append(RawDocument({
                        'doc': json.dumps(record),
                        'source': self.short_name,
                        'docID': doc_id,
                        'filetype': 'json'
                    }))
                else:
                    condition = False
            start += 10
        return doc_list
