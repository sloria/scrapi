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
from scrapi.linter.document import RawDocument, NormalizedDocument
from scrapi.base import BaseHarvester

logger = logging.getLogger(__name__)


class CrossRefHarvester(BaseHarvester):
    short_name = 'crossref'
    long_name = 'CrossRef'
    url = 'http://www.crossref.org'

    file_format = 'json'

    DEFAULT_ENCODING = 'UTF-8'

    record_encoding = None

    def copy_to_unicode(self, element):
        encoding = self.record_encoding or self.DEFAULT_ENCODING
        element = ''.join(element)
        if isinstance(element, unicode):
            return element
        else:
            return unicode(element, encoding=encoding)

    def harvest(self, days_back=0):
        start_date = date.today() - timedelta(days_back)
        base_url = 'http://api.crossref.org/v1/works?filter=from-pub-date:{},until-pub-date:{}&rows={{}}&offset={{}}'.format(str(start_date), str(date.today()))
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

    def get_contributors(self, doc):
        contributor_list = []
        contributor_dict_list = doc.get('author') or []
        full_names = []
        orcid = ''
        for entry in contributor_dict_list:
            full_name = '{} {}'.format(entry.get('given'), entry.get('family'))
            full_names.append(full_name)
            orcid = entry.get('ORCID') or ''
        for person in full_names:
            name = HumanName(person)
            contributor = {
                'prefix': name.title,
                'given': name.first,
                'middle': name.middle,
                'family': name.last,
                'suffix': name.suffix,
                'email': '',
                'ORCID': orcid
            }
            contributor_list.append(contributor)

        return contributor_list

    def get_ids(self, doc, raw_doc):
        ids = {}
        ids['url'] = doc.get('URL')
        ids['doi'] = doc.get('DOI')
        ids['serviceID'] = raw_doc.get('docID')
        return ids

    def get_properties(self, doc):
        properties = {
            'published-in': {
                'journalTitle': doc.get('container-title'),
                'volume': doc.get('volume'),
                'issue': doc.get('issue')
            },
            'publisher': doc.get('publisher'),
            'type': doc.get('type'),
            'ISSN': doc.get('ISSN'),
            'ISBN': doc.get('ISBN'),
            'member': doc.get('member'),
            'score': doc.get('score'),
            'issued': doc.get('issued'),
            'deposited': doc.get('deposited'),
            'indexed': doc.get('indexed'),
            'page': doc.get('page'),
            'issue': doc.get('issue'),
            'volume': doc.get('volume'),
            'referenceCount': doc.get('reference-count'),
            'updatePolicy': doc.get('update-policy'),
            'depositedTimestamp': doc['deposited'].get('timestamp')
        }
        return properties

    def get_tags(self, doc):
        tags = (((doc.get('subject') or []) + doc.get('container-title'))) or []
        return [tag.lower() for tag in tags]

    def get_date_updated(self, doc):
        issued_date_parts = doc['issued'].get('date-parts') or []
        date = ' '.join([str(part) for part in issued_date_parts[0]])
        isodateupdated = parse(date).isoformat()
        return self.copy_to_unicode(isodateupdated)

    def normalize(self, raw_doc):
        doc_str = raw_doc.get('doc')
        doc = json.loads(doc_str)

        normalized_dict = {
            'title': (doc.get('title') or [''])[0],
            'contributors': self.get_contributors(doc),
            'properties': self.get_properties(doc),
            'description': (doc.get('subtitle') or [''])[0],
            'id': self.get_ids(doc, raw_doc),
            'source': self.short_name,
            'dateUpdated': self.get_date_updated(doc),
            'tags': self.get_tags(doc)
        }

        return NormalizedDocument(normalized_dict)
