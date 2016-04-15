
from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class UWOHarvester(OAIHarvester):
    short_name = 'uwo'
    long_name = 'Western University'
    url = 'http://ir.lib.uwo.ca'

    base_url = 'http://ir.lib.uwo.ca/do/oai/'
    property_list = [
        'type', 'source', 'format', 'rights', 'identifier',
        'relation', 'date', 'description', 'setSpec'
    ]
