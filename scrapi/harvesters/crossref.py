"""
A CrossRef harvester for the SHARE project

Example API request: http://api.crossref.org/v1/works?filter=from-pub-date:2015-02-02,until-pub-date:2015-02-02&rows=1000
"""


## Harvester for the CrossRef metadata service
from __future__ import unicode_literals

import json
import logging

from datetime import date, timedelta

from nameparser import HumanName
from dateutil.parser import parse

from scrapi import requests
from scrapi import settings
from scrapi.base import JSONHarvester
from scrapi.base.helpers import build_properties
from scrapi.linter.document import RawDocument

logger = logging.getLogger(__name__)


def process_contributor(author, orcid):
    name = HumanName(author)
    return {
        'name': author,
        'givenName': name.first,
        'additionalName': name.middle,
        'familyName': name.last,
        'email': '',
        'sameAs': [orcid or '']
    }


class CrossRefHarvester(JSONHarvester):
    short_name = 'crossref'
    long_name = 'CrossRef'
    url = 'http://www.crossref.org'

    DEFAULT_ENCODING = 'UTF-8'

    record_encoding = None

    @property
    def schema(self):
        return {
            'title': ('/title', lambda x: x[0] if x else ''),
            'description': ('/subtitle', lambda x: x[0] if (isinstance(x, list) and x) else x or ''),
            'providerUpdatedDateTime': ('/issued/date-parts', lambda x: parse(' '.join([str(part) for part in x[0]])).date().isoformat().decode('utf-8')),
            'uris': {
                'canonicalUri': '/URL'
            },
            'contributors': ('/author', lambda x: [
                process_contributor(*[
                    '{} {}'.format(entry.get('given'), entry.get('family')),
                    entry.get('ORCID')
                ]) for entry in x
            ]),
            'otherProperties': build_properties(
                ('journalTitle', '/container-title'),
                ('volume', '/volume'),
                ('tags', ('/subject', '/container-title', lambda x, y: [tag.lower() for tag in (x or []) + (y or [])])),
                ('issue', '/issue'),
                ('publisher', '/publisher'),
                ('type', '/type'),
                ('ISSN', '/ISSN'),
                ('ISBN', '/ISBN'),
                ('member', '/member'),
                ('score', '/score'),
                ('issued', '/issued'),
                ('deposited', '/deposited'),
                ('indexed', '/indexed'),
                ('page', '/page'),
                ('issue', '/issue'),
                ('volume', '/volume'),
                ('referenceCount', '/reference-count'),
                ('updatePolicy', '/update-policy'),
                ('depositedTimestamp', '/deposited/timestamp')
            )
        }

    def harvest(self, start_date=None, end_date=None):
        start_date = start_date or date.today() - timedelta(settings.DAYS_BACK)
        end_date = end_date or date.today()

        base_url = 'http://api.crossref.org/v1/works?filter=from-pub-date:{},until-pub-date:{}&rows={{}}&offset={{}}'.format(start_date.isoformat(), end_date.isoformat())
        total = requests.get(base_url.format('0', '0')).json()['message']['total-results']
        logger.info('{} documents to be harvested'.format(total))

        doc_list = []
        for i in xrange(0, total, 1000):
            records = requests.get(base_url.format(1000, i)).json()['message']['items']
            logger.info('Harvested {} documents'.format(i + len(records)))

            for record in records:
                doc_id = record['DOI']
                doc_list.append(RawDocument({
                    'doc': json.dumps(record),
                    'source': self.short_name,
                    'docID': doc_id,
                    'filetype': 'json'
                }))

        return doc_list
