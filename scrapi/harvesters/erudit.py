'''
Harvester for the Erudit for the SHARE project

Example API call: http://oai.erudit.org/oai/?verb=ListRecords&metadataPrefix=oai_dc
'''
from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class EruditHarvester(OAIHarvester):
    short_name = 'erudit'
    long_name = 'Erudit'
    url = 'http://oai.erudit.org'

    base_url = 'http://oai.erudit.org/oai/'
    property_list = ['date', 'rights', 'identifier', 'relation', 'type', 'setSpec']
    timezone_granularity = True
