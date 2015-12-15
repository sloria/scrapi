'''
Harvester for the NCAR OpenSky Institutional Repository for the SHARE project

Example API call: http://opensky.ucar.edu/oai2?verb=ListRecords&metadataPrefix=oai_dc
'''
from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class UcarHarvester(OAIHarvester):
    short_name = 'ucar'
    long_name = 'NCAR OpenSky Institutional Repository'
    url = 'http://opensky.ucar.edu'

    base_url = 'http://opensky.ucar.edu/oai2'
    property_list = ['type', 'identifier', 'relation', 'rights', 'setSpec']
    approved_sets = [
        'archives_asr',
        'archives_srm',
        'archives_amsohp',
        'archives_atd',
        'research_books',
        'research_conference',
        'student_dcerc',
        'research_dataviz',
        'archives_fgge',
        'archives_gate',
        'archives_gtpr',
        'archives_hao',
        'archives_ucar',
        'archives_mesalab',
        'archives_ipcc',
        'archives_info',
        'archives_kuettner',
        'research_articles',
        'archives_lie',
        'opensky_archives',
    ]
    timezone_granularity = True
