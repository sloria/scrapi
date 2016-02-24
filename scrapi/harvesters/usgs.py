from __future__ import unicode_literals

import json
import logging
from datetime import date, timedelta, datetime
import six
import sys
import urllib2
from datetime import datetime
from decimal import Decimal
from nameparser import HumanName
from scrapi import requests, settings
from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument
from scrapi.base.helpers import default_name_parser, compose, build_properties, datetime_formatter

logger = logging.getLogger(__name__)


def process_contributors(authors):
    names = [author['text'] for author in authors]
    return default_name_parser(names)


class USGSHarvester(JSONHarvester):
    short_name = 'usgs'
    long_name = 'United States Geological Survey'
    url = 'https://pubs.er.usgs.gov/'
    DEFAULT_ENCODING = 'UTF-8'

    URL = 'https://pubs.er.usgs.gov/pubs-services/publication?'

    schema = {
        'title': '/title',
        'description': '/docAbstract',
        'providerUpdatedDateTime': ('/lastModifiedDate', datetime_formatter),
        'uris': {
            'canonicalUri': ('/id', 'https://pubs.er.usgs.gov/publication/{}'.format),
            'providerUris': [('/id', 'https://pubs.er.usgs.gov/publication/{}'.format)],
            'descriptorUris': [('/doi', 'https://dx.doi.org/{}'.format)]
        },
        'publisher': {
                'name': '/publisher'
            },
        'language': ['/language'],

        'contributors': ('/contributors/authors', compose(
            default_name_parser,
            lambda authors: [author['text'] for author in authors]
        )),
        'otherProperties': build_properties(
            ('serviceID', ('/id', str)),
            ('definedType', '/defined_type'),
            ('type', '/type'),
            ('links', '/links'),
            ('publishedDate', '/displayToPublicDate'),
            ('publicationYear', '/publicationYear'),
            ('issue', '/issue'),
            ('volume', '/volume'),
            ('language', '/language'),
            ('indexId', '/indexId'),
            ('publicationSubtype', '/publicationSubtype'),
            ('startPage', '/startPage'),
            ('endPage', '/endPage'),
            ('onlineOnly', '/onlineOnly'),
            ('additionalOnlineFiles', '/additionalOnlineFiles'),
            ('country', '/country'),
            ('state', '/state'),
            ('ipdsId', '/ipdsId'),
            ('otherGeospatial', '/otherGeospatial'),
            ('geographicExtents', '/geographicExtents'),

        )
    }

    def harvest(self, start_date=None, end_date=None):
        start_date = 2014
        end_date = 2015

        # if start_date > 0:
        #     url = "&startYear="+str(start_date)
        #     print url
        # if end_date> 0:
        #     url =  "&endYear="+str(end_date)
        #     print url
        #
        # # days_back = the number of days between start_date and now, defaulting to settings.DAYS_BACK
        days_back = 1 + settings.DAYS_BACK
        search_url = '{0}mod_x_days={1}'.format(
            self.URL,
            days_back,
        )
        search_url2 = "{}&startYear={}&endYear={}".format(self.URL, start_date, end_date)
        return [
            RawDocument({
                'doc': json.dumps(record),
                'source': self.short_name,
                'docID': six.text_type(record['id']),
                'filetype': 'json'
            }) for record in self.get_records(search_url, search_url2)
            ]

    def get_records(self, search_url, search_url2):
        records = requests.get(search_url, search_url2)
        total_records = records.json()['recordCount']
        logger.info('Harvesting {} records'.format(total_records))
        page_number = 1
        count = 0

        while records.json()['records']:
            record_list = records.json()['records']
            for record in record_list:
                count += 1
                yield record

            page_number += 1
            records = requests.get(search_url + '&page_number={}'.format(page_number))
            logger.info('{} documents harvested'.format(count))
