""""
A Fake harvester for the SHARE project

NOTE: This harvester will do NOTHING unless scrapi.settings.local.DEBUG is set.

Does not connect to any external repositories. This harvester generates
fake JSON documents for testing and learning purposes.

Example API request: none! FakeJSONHarvester generates JSON documents.
"""

# TODO: This harvester should be suppressed in production. Recommend
# detecting a production flag in settings.local and returning empty results.

from __future__ import unicode_literals

import json
import logging

from dateutil.parser import parse

from scrapi.base import JSONHarvester
from scrapi.linter.document import RawDocument
from scrapi.settings import local

logger = logging.getLogger(__name__)


def process_contributor(entry):
    given, family = entry
    return {
        'name': ' '.join(entry),
        'givenName': given,
        'additionalName': '',
        'familyName': family,
        'email': '',
        'sameAs': ['']
    }


class FakeJSONHarvester(JSONHarvester):
    short_name = 'fakejson'
    long_name = 'FakeJSONHarvester'
    url = 'http://localhost:4242'  # going nowhere

    DEFAULT_ENCODING = 'UTF-8'

    record_encoding = None

    @property
    def schema(self):
        return {
            'title': ('/title', lambda x: x[0] if x else ''),
            'providerUpdatedDateTime': (
                '/date/date-parts',
                lambda x:
                    parse(
                        ' '.join([str(part) for part in x[0]])
                    ).date().isoformat().decode('utf-8') + 'T00:00:00+00:00'
            ),
            'uris': {
                'canonicalUri': '/URL'
            },
            'contributors': ('/authors', lambda x: [
                process_contributor(entry) for entry in x
            ])
        }

    def harvest(self, days_back=0):
        """Typically, you need to define base URL and fetch it multiple
        times with different page ranges. Each fetch will return a JSON
        containing a list of documents. See harvesters.crossref.harvest.
        In this case, we just fake it..."""

        if local.DEBUG:
            total = 4 if days_back == 0 else min(4, 2 * days_back)
        else:
            total = 0
        logger.info('{} documents to be harvested'.format(total))

        doc_list = []
        for i in xrange(total):
            doc = RawDocument({
                'doc': fake_json(i),
                'source': self.short_name,
                'docID': 'fake-json-{}'.format(i),  # normally fetched/parsed
                'filetype': 'json'
            })
            doc_list.append(doc)
        return doc_list


def fake_json(num):
    logger.info('fake_json({})'.format(num))
    result = json.dumps({
        'title': ['Fake JSON document {}'.format(num)],
        'date': {
            'date-parts': [
                [
                    2015,
                    1,
                    num + 1
                ]
            ]
        },
        'URL': 'nowhere',
        'authors': [
            ('Jane', 'Doe'),
            ('John', 'Smith'),
        ]
    })
    logger.info(result)
    return result
