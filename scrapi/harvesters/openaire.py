'''
Harvester for the OAI-PMH Publisher for OpenAIRE+. Powered by D-NET. for the SHARE project

Example API call: http://api.openaire.eu/oai_pmh?verb=ListRecords&metadataPrefix=oai_dc
'''
from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class OpenaireHarvester(OAIHarvester):
    short_name = 'openaire'
    long_name = 'OAI-PMH Publisher for OpenAIRE+. Powered by D-NET.'
    url = 'http://api.openaire.eu'

    base_url = 'http://api.openaire.eu/oai_pmh'
    property_list = ['rights', 'source', 'relation', 'date', 'identifier', 'type', 'setSpec']
    timezone_granularity = True
