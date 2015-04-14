""""
A Fake harvester for the SHARE project

NOTE: This harvester will do NOTHING unless scrapi.settings.local.DEBUG is set.

Does not connect to any external repositories. This harvester generates
fake HTML documents for testing and learning purposes.

Example API request: none! FakeXMLHarvester generates XML documents.
"""

# TODO: This harvester should be suppressed in production. Recommend
# detecting a production flag in settings.local and returning empty results.

from __future__ import unicode_literals

import logging
import textwrap

from dateutil.parser import parse

from scrapi.base import XMLHarvester
from scrapi.linter.document import RawDocument
from scrapi.settings import local

logger = logging.getLogger(__name__)


def process_contributors(author_elements):
    result = []
    for author_element in author_elements:
        family_names = author_element.xpath('family_name/text()')
        family_name = grab_first_and_only('family_names', family_names)
        given_names = author_element.xpath('given_name/text()')
        given_name = grab_first_and_only('given_names', given_names)
        result.append({
            'name': '{} {}'.format(given_name, family_name),
            'givenName': given_name,
            'additionalName': '',
            'familyName': family_name,
            'email': '',
            'sameAs': ['']
        })
    return result


def process_title(titles):
    return grab_first_and_only('titles', titles)


def grab_first_and_only(sequence_message, sequence):
    if not sequence:
        logger.info('%s is empty', sequence_message)
        return ''
    if len(sequence) > 1:
        logger.info('%s has more than one element: %s',
                    sequence_message, sequence)
    return sequence[0]


class FakeXMLHarvester(XMLHarvester):
    short_name = 'fakexml'
    long_name = 'FakeXMLHarvester'
    url = 'http://localhost:4242'  # going nowhere

    DEFAULT_ENCODING = 'UTF-8'

    record_encoding = None

    namespaces = {}  # Needed for XML harvesters

    @property
    def schema(self):
        return {
            'title': ('/record/title/text()', process_title),
            'providerUpdatedDateTime': (
                '/record/date/*/text()',
                lambda x:
                    parse(
                        ' '.join([str(part) for part in x])
                    ).date().isoformat().decode('utf-8') + 'T00:00:00+00:00'
            ),
            'uris': {
                'canonicalUri': '/record/URL/text()'
            },
            'contributors': (
                '/record/authors/author/.',
                process_contributors
            )
        }

    def harvest(self, days_back=0):
        """Typically, you need to define base URL and fetch it multiple
        times with different page ranges. Each fetch will return a XML
        containing a list of documents. See harvesters.crossref.harvest.
        In this case, we just fake it..."""

        if local.DEBUG:
            total = 4 if days_back == 0 else min(4, 2 * days_back)
        else:
            total = 0  # Do nothing if not in DEBUG (development) mode.
        logger.info('{} documents to be harvested'.format(total))

        doc_list = []
        for i in xrange(total):
            doc = RawDocument({
                'doc': fake_xml(i),
                'source': self.short_name,
                'docID': 'fake-xml-{}'.format(i),  # normally fetched/parsed
                'filetype': 'xml'
            })
            doc_list.append(doc)
        return doc_list


def fake_xml(num):
    """Generate a fake XML document."""
    logger.info('fake_xml({})'.format(num))
    result = textwrap.dedent(
        '''
        <record>
          <title>Fake XML document {}</title>
          <date>
            <year>2015</year>
            <month>1</month>
            <day>{}</day>
          </date>
          <URL>nowhere</URL>
          <authors>
            <author>
              <given_name>Jane</given_name>
              <family_name>Doe</family_name>
            </author>
            <author>
              <given_name>Spock</given_name>
            </author>
            <author>
              <given_name>John</given_name>
              <family_name>Smith</family_name>
            </author>
          </authors>
        </record>
        '''[1:]
    ).format(num, num + 1)
    logger.debug(repr(result))
    return result
