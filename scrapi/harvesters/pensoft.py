"""
Harvester for repositories in Pensoft for the SHARE project

Example API calls for each service in each harvester
"""


from __future__ import unicode_literals

from furl import furl
from lxml import etree
from datetime import timedelta, date

from scrapi import settings
from scrapi import util
from scrapi.base import OAIHarvester
from scrapi.linter.document import RawDocument


class PensoftHarvester(OAIHarvester):

    @property
    def base_url(self):
        return 'http://{short}.pensoft.net/oai.php/?set={short}'.format(short=self.short_name)

    @property
    def url(self):
        return 'http://{short}.pensoft.net'.format(short=self.short_name)

    property_list = ['format', 'rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = False

    # don't include the end date for pensoft harvesters
    def harvest(self, start_date=None, end_date=None):

        start_date = (start_date or date.today() - timedelta(settings.DAYS_BACK)).isoformat()
        end_date = (end_date or date.today()).isoformat()

        furled_baseurl = furl(self.base_url)
        furled_baseurl.args['verb'] = 'ListRecords'
        furled_baseurl.args['metadataPrefix'] = 'oai_dc'
        furled_baseurl.args['from'] = start_date

        records = self.get_records(furled_baseurl.url, start_date)

        return [
            RawDocument({
                'doc': etree.tostring(record, encoding=self.record_encoding),
                'source': self.short_name,
                'docID': record.xpath('ns0:header/ns0:identifier', namespaces=self.namespaces)[0].text,
                'filetype': 'xml'
            }) for record in records
        ]


class BiodiversityDataJournalHarvester(PensoftHarvester):
    '''Harvester for Biodiversity Data Journal
    Sample API Call = http://bdj.pensoft.net/oai.php?set=bdj&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'bdj'
    long_name = 'Biodiversity Data Journal'


class ZooKeysHarvester(PensoftHarvester):
    '''Harvester for ZooKeys
    Sample API Call = http://zookeys.pensoft.net/oai.php?set=zookeys&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'zookeys'
    long_name = 'ZooKeys'


class PhytoKeysHarvester(PensoftHarvester):
    '''Harvester for PhytoKeys
    Sample API Call = http://phytokeys.pensoft.net/oai.php?set=phytokeys&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'phytokeys'
    long_name = 'PhytoKeys'


class MycoKeysHarvester(PensoftHarvester):
    '''Harvester for MycoKeys
    Sample API Call = http://mycokeys.pensoft.net/oai.php?set=mycokeys&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'mycokeys'
    long_name = 'MycoKeys'


class BioRiskHarvester(PensoftHarvester):
    '''Harvester for BioRisk
    Sample API Call = http://biorisk.pensoft.net/oai.php?set=biorisk&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'biorisk'
    long_name = 'BioRisk'


class ComparativeCytogeneticsHarvester(PensoftHarvester):
    '''Harvester for Comparative Cytogenetics
    Sample API Call = http://compcytogen.pensoft.net/oai.php?set=compcytogen&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'compcytogen'
    long_name = 'Comparative Cytogenetics'


class InternationalJournalofMyriapodologyHarvester(PensoftHarvester):
    '''Harvester for International Journal of Myriapodology
    Sample API Call = http://ijm.pensoft.net/oai.php?set=ijm&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'ijm'
    long_name = 'International Journal of Myriapodology'


class JournalofHymenopteraResearchHarvester(PensoftHarvester):
    '''Harvester for Journal of Hymenoptera Research
    Sample API Call = http://jhr.pensoft.net/oai.php?set=jhr&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'jhr'
    long_name = 'Journal of Hymenoptera Research'


class NatureConservationHarvester(PensoftHarvester):
    '''Harvester for Nature Conservation
    Sample API Call = http://natureconservation.pensoft.net/oai.php?set=natureconservation&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'natureconservation'
    long_name = 'Nature Conservation'


class NeoBiotaHarvester(PensoftHarvester):
    '''Harvester for NeoBiota
    Sample API Call = http://neobiota.pensoft.net/oai.php?set=neobiota&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'neobiota'
    long_name = 'NeoBiota'


class SubterraneanBiologyHarvester(PensoftHarvester):
    '''Harvester for Subterranean Biology
    Sample API Call = http://subtbiol.pensoft.net/oai.php?set=subtbiol&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'subtbiol'
    long_name = 'Subterranean Biology'


class DeutscheEntomologischeZeitschriftHarvester(PensoftHarvester):
    '''Harvester for Deutsche Entomologische Zeitschrift
    Sample API Call = http://dez.pensoft.net/oai.php?set=dez&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'dez'
    long_name = 'Deutsche Entomologische Zeitschrift'


class ZoosystematicsandEvolutionHarvester(PensoftHarvester):
    '''Harvester for Zoosystematics and Evolution
    Sample API Call = http://zse.pensoft.net/oai.php?set=zse&verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'zse'
    long_name = 'Zoosystematics and Evolution'
