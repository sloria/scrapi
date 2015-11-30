# Classes for scrAPI Harvesters
from __future__ import unicode_literals

import abc
import json
import logging
from datetime import timedelta, date

import six
from furl import furl
from lxml import etree

from scrapi import requests
from scrapi import registry
from scrapi import settings
from scrapi.base.schemas import OAISCHEMA
from scrapi.linter.document import RawDocument, NormalizedDocument
from scrapi.base.transformer import XMLTransformer, JSONTransformer
from scrapi.base.helpers import (
    updated_schema,
    build_properties,
    oai_get_records_and_token,
    compose,
    datetime_formatter,
    null_on_error,
    coerce_to_list
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

etree.set_default_parser(etree.XMLParser(recover=True))


class HarvesterMeta(abc.ABCMeta):
    def __init__(cls, name, bases, dct):
        super(HarvesterMeta, cls).__init__(name, bases, dct)
        if len(cls.__abstractmethods__) == 0 and cls.short_name not in settings.disabled:
            registry[cls.short_name] = cls()
        else:
            logger.info('Class {} not added to registry'.format(cls.__name__))


@six.add_metaclass(HarvesterMeta)
class BaseHarvester(object):
    """ This is a base class that all harvesters should inheret from

    Defines the copy to unicode method, which is useful for getting standard
    unicode out of xml results.
    """

    @abc.abstractproperty
    def short_name(self):
        raise NotImplementedError

    @abc.abstractproperty
    def long_name(self):
        raise NotImplementedError

    @abc.abstractproperty
    def url(self):
        raise NotImplementedError

    @abc.abstractproperty
    def file_format(self):
        raise NotImplementedError

    @abc.abstractmethod
    def harvest(self, start_date=None, end_date=None):
        raise NotImplementedError

    @abc.abstractmethod
    def normalize(self, raw_doc):
        raise NotImplementedError

    @property
    def run_at(self):
        return {
            'hour': 22,
            'minute': 59,
            'day_of_week': 'mon-sun',
        }


class JSONHarvester(BaseHarvester, JSONTransformer):
    file_format = 'json'

    def normalize(self, raw_doc):
        transformed = self.transform(json.loads(raw_doc['doc']), fail=settings.RAISE_IN_TRANSFORMER)
        transformed['shareProperties'] = {
            'source': self.short_name,
            'docID': raw_doc['docID'],
            'filetype': raw_doc['filetype']
        }
        return NormalizedDocument(transformed, clean=True)


class XMLHarvester(BaseHarvester, XMLTransformer):
    file_format = 'xml'

    def normalize(self, raw_doc):
        transformed = self.transform(etree.XML(raw_doc['doc']), fail=settings.RAISE_IN_TRANSFORMER)
        transformed['shareProperties'] = {
            'source': self.short_name,
            'docID': raw_doc['docID'],
            'filetype': raw_doc['filetype']
        }
        return NormalizedDocument(transformed, clean=True)


class AutoOAIHarvester(XMLHarvester):
    """ Take a given URL and approved sets, and harvest everything that repo
    has on the sets from all available
    """

    _identify_element = None
    _timezone_granularity = None
    _metadata_prefixes = None
    _property_list = None
    _record_encoding = None

    timeout = 0.5
    approved_sets = None
    timezone_granularity = False
    property_list = ['date', 'type']
    force_request_update = False
    verify = True
    all_namespaces = {}

    def namespaces(self, element):
        namespaces = element.nsmap

        for key, value in namespaces.items():
            if not key:
                namespaces['ns0'] = value
        namespaces.pop(None)
        self.all_namespaces.update(namespaces)
        print('UPDATING NSPS WITH {}'.format(namespaces))
        return namespaces

    @property
    def identify_element(self):
        if self._identify_element:
            return self._identify_element
        url = furl(self.base_url)
        url.args['verb'] = 'Identify'
        self._identify_element = etree.XML(requests.get(url.url).content)

        return self._identify_element

    @property
    def metadata_prefixes(self):
        if self._metadata_prefixes:
            return self._metadata_prefixes
        url = furl(self.base_url)
        url.args['verb'] = 'ListMetadataFormats'
        xml_content = etree.XML(requests.get(url.url).content)
        namespaces = self.namespaces(xml_content)
        self._metadata_prefixes = xml_content.xpath('//ns0:metadataPrefix/node()', namespaces=namespaces)

        return self._metadata_prefixes

    @property
    def record_encoding(self):
        if self._record_encoding:
            return self._record_encoding
        url = furl(self.base_url)
        url.args['verb'] = 'Identify'

        self._record_encoding = requests.get(url.url).encoding
        return self._record_encoding

    @property
    def long_name(self):
        namespaces = self.namespaces(self.identify_element)
        return self.identify_element.xpath('//ns0:repositoryName/node()', namespaces=namespaces)

    @property
    def timezone_granularity(self):
        if self._timezone_granularity:
            return self._timezone_granularity
        namespaces = self.namespaces(self.identify_element)
        granularity = self.identify_element.xpath('//ns0:granularity/node()', namespaces=namespaces)

        if 'hh:mm:ss' in granularity:
            return True
        else:
            return False

    @property
    def schema(self):
        return self._schema

    @property
    def _schema(self):
        return updated_schema(OAISCHEMA, self.formatted_properties)

    @property
    def formatted_properties(self):
        return {
            'otherProperties': build_properties(
                *list(
                    map(
                        self.format_property,
                        self.property_list
                    )
                )
            )
        }

    def format_property(self, property):
        if property == 'date':
            null_on_error(datetime_formatter)
            fn = compose(lambda x: list(
                map(
                    null_on_error(datetime_formatter),
                    x
                )
            ), coerce_to_list, self.resolve_property)
        else:
            fn = self.resolve_property
        inner_tuple = ['//{}:{}/node()'.format(namespace, property) for namespace in self.all_namespaces]
        inner_tuple.append(fn)
        return (property, tuple(inner_tuple))

    def resolve_property(self, *args):
        ret = [item for sublist in args for item in sublist]
        return ret[0] if len(ret) == 1 else ret

    def get_identifiers(self, identifiers_url):
        identifier_content = requests.get(identifiers_url).content
        identifiers = etree.XML(identifier_content)
        return identifiers.xpath('//ns0:identifier/node()', namespaces=self.namespaces(identifiers))

    def get_record(self, record_url):
        record_content = requests.get(record_url, throttle=0.5).content
        record_xml = etree.XML(record_content)

        # make sure we add all of the namespaces to all_namespaces
        metadata = record_xml.xpath('//ns0:metadata', namespaces=self.namespaces(record_xml))
        for child in metadata[0].getchildren():
            self.namespaces(child)
        self.namespaces(record_xml)

        return record_xml

    def harvest(self, start_date=None, end_date=None):
        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        url = furl(self.base_url)

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        records = []
        # Get a list of all identifiers for each metadata prefix given the date range
        for prefix in self.metadata_prefixes:
            print('checking out the prefix {}'.format(prefix))
            url.args['verb'] = 'ListIdentifiers'
            url.args['metadataPrefix'] = prefix
            url.args['from'] = start_date
            url.args['until'] = end_date
            prefix_ids = self.get_identifiers(url.url)

            url.args.pop('from')
            url.args.pop('until')
            # request each of those identifiers records for that prefix
            for identifier in prefix_ids:
                url.args['verb'] = 'GetRecord'
                url.args['identifier'] = identifier

                records.append(self.get_record(url.url))

                # For testing only!
                if len(records) % 3 == 0:
                    print('Collected {} records...'.format(len(records)))
        return [
            RawDocument({
                'doc': etree.tostring(record, encoding=self.record_encoding),
                'source': self.short_name,
                'docID': record.xpath('//ns0:header/ns0:identifier', namespaces=self.namespaces(record))[0].text,
                'filetype': 'xml'
            }) for record in records
        ]

    def normalize(self, raw_doc):
        str_result = raw_doc.get('doc')
        result = etree.XML(str_result)

        if self.approved_sets:
            set_spec = result.xpath(
                '//ns0:header/ns0:setSpec/node()',
                namespaces=self.namespaces
            )
            # check if there's an intersection between the approved sets and the
            # setSpec list provided in the record. If there isn't, don't normalize.
            if not {x.replace('publication:', '') for x in set_spec}.intersection(self.approved_sets):
                logger.info('Series {} not in approved list'.format(set_spec))
                return None

        status = result.xpath('//ns0:header/@status', namespaces=self.namespaces(result))
        if status and status[0] == 'deleted':
            logger.info('Deleted record, not normalizing {}'.format(raw_doc['docID']))
            return None

        return super(AutoOAIHarvester, self).normalize(raw_doc)


class OAIHarvester(XMLHarvester):
    """ Create a harvester with a oai_dc namespace, that will harvest
    documents within a certain date range

    Contains functions for harvesting from an OAI provider, normalizing,
    and outputting in a way that scrapi can understand, in the most
    generic terms possible.

    For more information, see the OAI PMH specification:
    http://www.openarchives.org/OAI/openarchivesprotocol.html
    """
    record_encoding = None
    DEFAULT_ENCODING = 'UTF-8'
    RESUMPTION = '&resumptionToken='
    RECORDS_URL = '?verb=ListRecords'
    META_PREFIX_DATE = '&metadataPrefix=oai_dc&from={}&until={}'

    # Override these variable is required
    namespaces = {
        'dc': 'http://purl.org/dc/elements/1.1/',
        'ns0': 'http://www.openarchives.org/OAI/2.0/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/',
    }

    timeout = 0.5
    approved_sets = None
    timezone_granularity = False
    property_list = ['date', 'type']
    force_request_update = False
    verify = True

    @property
    def schema(self):
        return self._schema

    @property
    def _schema(self):
        return updated_schema(OAISCHEMA, self.formatted_properties)

    @property
    def formatted_properties(self):
        return {
            'otherProperties': build_properties(
                *list(
                    map(
                        self.format_property,
                        self.property_list)))}

    def format_property(self, property):
        if property == 'date':
            force_date = null_on_error(datetime_formatter)
            fn = compose(lambda x: list(
                map(
                    null_on_error(datetime_formatter),
                    x
                )
            ), coerce_to_list, self.resolve_property)
        else:
            fn = self.resolve_property
        return (property, (
            '//dc:{}/node()'.format(property),
            '//ns0:{}/node()'.format(property),
            fn)
        )

    def resolve_property(self, dc, ns0):
        ret = dc + ns0
        return ret[0] if len(ret) == 1 else ret

    def harvest(self, start_date=None, end_date=None):
        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        url.args['until'] = end_date

        records = self.get_records(url.url, start_date, end_date)

        return [
            RawDocument({
                'doc': etree.tostring(record, encoding=self.record_encoding),
                'source': self.short_name,
                'docID': record.xpath('ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text,
                'filetype': 'xml'
            }) for record in records
        ]

    def get_records(self, url, start_date, end_date=None):
        url = furl(url)
        all_records, token = oai_get_records_and_token(url.url, self.timeout, self.force_request_update, self.namespaces, self.verify)

        while token:
            url.remove('from')
            url.remove('until')
            url.remove('metadataPrefix')
            url.args['resumptionToken'] = token[0]
            records, token = oai_get_records_and_token(url.url, self.timeout, self.force_request_update, self.namespaces, self.verify)
            all_records += records

        return all_records

    def normalize(self, raw_doc):
        str_result = raw_doc.get('doc')
        result = etree.XML(str_result)

        if self.approved_sets:
            set_spec = result.xpath(
                'ns0:header/ns0:setSpec/node()',
                namespaces=self.namespaces
            )
            # check if there's an intersection between the approved sets and the
            # setSpec list provided in the record. If there isn't, don't normalize.
            if not {x.replace('publication:', '') for x in set_spec}.intersection(self.approved_sets):
                logger.info('Series {} not in approved list'.format(set_spec))
                return None

        status = result.xpath('ns0:header/@status', namespaces=self.namespaces)
        if status and status[0] == 'deleted':
            logger.info('Deleted record, not normalizing {}'.format(raw_doc['docID']))
            return None

        return super(OAIHarvester, self).normalize(raw_doc)
