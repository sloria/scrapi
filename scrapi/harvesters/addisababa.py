'''
Harvester for the Addis Ababa University Libraries Electronic Thesis and Dissertations: AAU-ETD! for the SHARE project

Example API call: http://etd.aau.edu.et/dspace-oai/request?verb=ListRecords&metadataPrefix=oai_dc
'''
from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class AddisababaHarvester(OAIHarvester):
    short_name = 'addisababa'
    long_name = 'Addis Ababa University Libraries Electronic Thesis and Dissertations: AAU-ETD!'
    url = 'http://etd.aau.edu.et/dspace/'

    base_url = 'http://etd.aau.edu.et/dspace-oai/request'
    property_list = ['date', 'identifier', 'type', 'setSpec']
    timezone_granularity = True
