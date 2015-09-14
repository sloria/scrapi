"""
Harvester for repositories in Pensoft for the SHARE project

Example API calls for each service in each harvester
"""


from __future__ import unicode_literals

import furl
from lxml import etree
from datetime import timedelta, date

from scrapi import util
from scrapi import settings
from scrapi.base import OAIHarvester
from scrapi.linter.document import RawDocument


class BiodiversityDataJournalHarvester(OAIHarvester):
    '''Harvester for Biodiversity Data Journal
    Sample API Call = http://bdj.pensoft.net/oai.php?set=bdj?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'bdj'
    long_name = 'Biodiversity Data Journal'
    url = 'http://bdj.pensoft.net'

    base_url = 'http://bdj.pensoft.net/oai.php?set=bdj'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class ZooKeysHarvester(OAIHarvester):
    '''Harvester for ZooKeys
    Sample API Call = http://zookeys.pensoft.net/oai.php?set=zookeys?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'zookeys'
    long_name = 'ZooKeys'
    url = 'http://zookeys.pensoft.net'

    base_url = 'http://zookeys.pensoft.net/oai.php?set=zookeys'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class PhytoKeysHarvester(OAIHarvester):
    '''Harvester for PhytoKeys
    Sample API Call = http://phytokeys.pensoft.net/oai.php?set=phytokeys?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'phytokeys'
    long_name = 'PhytoKeys'
    url = 'http://phytokeys.pensoft.net'

    base_url = 'http://phytokeys.pensoft.net/oai.php?set=phytokeys'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class MycoKeysHarvester(OAIHarvester):
    '''Harvester for MycoKeys
    Sample API Call = http://mycokeys.pensoft.net/oai.php?set=mycokeys?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'mycokeys'
    long_name = 'MycoKeys'
    url = 'http://mycokeys.pensoft.net'

    base_url = 'http://mycokeys.pensoft.net/oai.php?set=mycokeys'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class BioRiskHarvester(OAIHarvester):
    '''Harvester for BioRisk
    Sample API Call = http://biorisk.pensoft.net/oai.php?set=biorisk?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'biorisk'
    long_name = 'BioRisk'
    url = 'http://biorisk.pensoft.net'

    base_url = 'http://biorisk.pensoft.net/oai.php?set=biorisk'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class ComparativeCytogeneticsHarvester(OAIHarvester):
    '''Harvester for Comparative Cytogenetics
    Sample API Call = http://compcytogen.pensoft.net/oai.php?set=compcytogen?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'compcytogen'
    long_name = 'Comparative Cytogenetics'
    url = 'http://compcytogen.pensoft.net'

    base_url = 'http://compcytogen.pensoft.net/oai.php?set=compcytogen'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class InternationalJournalofMyriapodologyHarvester(OAIHarvester):
    '''Harvester for International Journal of Myriapodology
    Sample API Call = http://ijm.pensoft.net/oai.php?set=ijm?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'ijm'
    long_name = 'International Journal of Myriapodology'
    url = 'http://ijm.pensoft.net'

    base_url = 'http://ijm.pensoft.net/oai.php?set=ijm'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class JournalofHymenopteraResearchHarvester(OAIHarvester):
    '''Harvester for Journal of Hymenoptera Research
    Sample API Call = http://jhr.pensoft.net/oai.php?set=jhr?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'jhr'
    long_name = 'Journal of Hymenoptera Research'
    url = 'http://jhr.pensoft.net'

    base_url = 'http://jhr.pensoft.net/oai.php?set=jhr'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class NatureConservationHarvester(OAIHarvester):
    '''Harvester for Nature Conservation
    Sample API Call = http://natureconservation.pensoft.net/oai.php?set=natureconservation?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'natureconservation'
    long_name = 'Nature Conservation'
    url = 'http://natureconservation.pensoft.net'

    base_url = 'http://natureconservation.pensoft.net/oai.php?set=natureconservation'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class NeoBiotaHarvester(OAIHarvester):
    '''Harvester for NeoBiota
    Sample API Call = http://neobiota.pensoft.net/oai.php?set=neobiota?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'neobiota'
    long_name = 'NeoBiota'
    url = 'http://neobiota.pensoft.net'

    base_url = 'http://neobiota.pensoft.net/oai.php?set=neobiota'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class SubterraneanBiologyHarvester(OAIHarvester):
    '''Harvester for Subterranean Biology
    Sample API Call = http://subtbiol.pensoft.net/oai.php?set=subtbiol?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'subtbiol'
    long_name = 'Subterranean Biology'
    url = 'http://subtbiol.pensoft.net'

    base_url = 'http://subtbiol.pensoft.net/oai.php?set=subtbiol'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class DeutscheEntomologischeZeitschriftHarvester(OAIHarvester):
    '''Harvester for Deutsche Entomologische Zeitschrift
    Sample API Call = http://dez.pensoft.net/oai.php?set=dez?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'dez'
    long_name = 'Deutsche Entomologische Zeitschrift'
    url = 'http://dez.pensoft.net'

    base_url = 'http://dez.pensoft.net/oai.php?set=dez'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list


class ZoosystematicsandEvolutionHarvester(OAIHarvester):
    '''Harvester for Zoosystematics and Evolution
    Sample API Call = http://zse.pensoft.net/oai.php?set=zse?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'zse'
    long_name = 'Zoosystematics and Evolution'
    url = 'http://zse.pensoft.net'

    base_url = 'http://zse.pensoft.net/oai.php?set=zse'
    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        if self.timezone_granularity:
            start_date += 'T00:00:00Z'
            end_date += 'T00:00:00Z'

        url = furl.furl(self.base_url)
        url.args['verb'] = 'ListRecords'
        url.args['metadataPrefix'] = 'oai_dc'
        url.args['from'] = start_date
        # don't include the end date for pensoft harvesters

        records = self.get_records(url.url, start_date)

        rawdoc_list = []
        for record in records:
            doc_id = record.xpath(
                'ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text
            record = etree.tostring(record, encoding=self.record_encoding)
            rawdoc_list.append(RawDocument({
                'doc': record,
                'source': util.copy_to_unicode(self.short_name),
                'docID': util.copy_to_unicode(doc_id),
                'filetype': 'xml'
            }))

        return rawdoc_list
