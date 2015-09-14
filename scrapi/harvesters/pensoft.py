"""
Harvester for repositories in Pensoft for the SHARE project

Example API calls for each service in each harvester
"""


from __future__ import unicode_literals


from scrapi.base import PensoftHarvester


class BiodiversityDataJournalHarvester(PensoftHarvester):
    '''Harvester for Biodiversity Data Journal
    Sample API Call = http://bdj.pensoft.net/oai.php?set=bdj?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'bdj'
    long_name = 'Biodiversity Data Journal'
    url = 'http://bdj.pensoft.net'

    base_url = 'http://bdj.pensoft.net/oai.php?set=bdj'


class ZooKeysHarvester(PensoftHarvester):
    '''Harvester for ZooKeys
    Sample API Call = http://zookeys.pensoft.net/oai.php?set=zookeys?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'zookeys'
    long_name = 'ZooKeys'
    url = 'http://zookeys.pensoft.net'

    base_url = 'http://zookeys.pensoft.net/oai.php?set=zookeys'


class PhytoKeysHarvester(PensoftHarvester):
    '''Harvester for PhytoKeys
    Sample API Call = http://phytokeys.pensoft.net/oai.php?set=phytokeys?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'phytokeys'
    long_name = 'PhytoKeys'
    url = 'http://phytokeys.pensoft.net'

    base_url = 'http://phytokeys.pensoft.net/oai.php?set=phytokeys'


class MycoKeysHarvester(PensoftHarvester):
    '''Harvester for MycoKeys
    Sample API Call = http://mycokeys.pensoft.net/oai.php?set=mycokeys?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'mycokeys'
    long_name = 'MycoKeys'
    url = 'http://mycokeys.pensoft.net'

    base_url = 'http://mycokeys.pensoft.net/oai.php?set=mycokeys'


class BioRiskHarvester(PensoftHarvester):
    '''Harvester for BioRisk
    Sample API Call = http://biorisk.pensoft.net/oai.php?set=biorisk?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'biorisk'
    long_name = 'BioRisk'
    url = 'http://biorisk.pensoft.net'

    base_url = 'http://biorisk.pensoft.net/oai.php?set=biorisk'


class ComparativeCytogeneticsHarvester(PensoftHarvester):
    '''Harvester for Comparative Cytogenetics
    Sample API Call = http://compcytogen.pensoft.net/oai.php?set=compcytogen?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'compcytogen'
    long_name = 'Comparative Cytogenetics'
    url = 'http://compcytogen.pensoft.net'

    base_url = 'http://compcytogen.pensoft.net/oai.php?set=compcytogen'


class InternationalJournalofMyriapodologyHarvester(PensoftHarvester):
    '''Harvester for International Journal of Myriapodology
    Sample API Call = http://ijm.pensoft.net/oai.php?set=ijm?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'ijm'
    long_name = 'International Journal of Myriapodology'
    url = 'http://ijm.pensoft.net'

    base_url = 'http://ijm.pensoft.net/oai.php?set=ijm'


class JournalofHymenopteraResearchHarvester(PensoftHarvester):
    '''Harvester for Journal of Hymenoptera Research
    Sample API Call = http://jhr.pensoft.net/oai.php?set=jhr?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'jhr'
    long_name = 'Journal of Hymenoptera Research'
    url = 'http://jhr.pensoft.net'

    base_url = 'http://jhr.pensoft.net/oai.php?set=jhr'


class NatureConservationHarvester(PensoftHarvester):
    '''Harvester for Nature Conservation
    Sample API Call = http://natureconservation.pensoft.net/oai.php?set=natureconservation?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'natureconservation'
    long_name = 'Nature Conservation'
    url = 'http://natureconservation.pensoft.net'

    base_url = 'http://natureconservation.pensoft.net/oai.php?set=natureconservation'


class NeoBiotaHarvester(PensoftHarvester):
    '''Harvester for NeoBiota
    Sample API Call = http://neobiota.pensoft.net/oai.php?set=neobiota?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'neobiota'
    long_name = 'NeoBiota'
    url = 'http://neobiota.pensoft.net'

    base_url = 'http://neobiota.pensoft.net/oai.php?set=neobiota'


class SubterraneanBiologyHarvester(PensoftHarvester):
    '''Harvester for Subterranean Biology
    Sample API Call = http://subtbiol.pensoft.net/oai.php?set=subtbiol?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'subtbiol'
    long_name = 'Subterranean Biology'
    url = 'http://subtbiol.pensoft.net'

    base_url = 'http://subtbiol.pensoft.net/oai.php?set=subtbiol'


class DeutscheEntomologischeZeitschriftHarvester(PensoftHarvester):
    '''Harvester for Deutsche Entomologische Zeitschrift
    Sample API Call = http://dez.pensoft.net/oai.php?set=dez?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'dez'
    long_name = 'Deutsche Entomologische Zeitschrift'
    url = 'http://dez.pensoft.net'

    base_url = 'http://dez.pensoft.net/oai.php?set=dez'


class ZoosystematicsandEvolutionHarvester(PensoftHarvester):
    '''Harvester for Zoosystematics and Evolution
    Sample API Call = http://zse.pensoft.net/oai.php?set=zse?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = 'zse'
    long_name = 'Zoosystematics and Evolution'
    url = 'http://zse.pensoft.net'

    base_url = 'http://zse.pensoft.net/oai.php?set=zse'
