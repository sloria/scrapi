"""
Harvester for the eScholarship repository at the University of California for the SHARE project

More information available here:
https://github.com/CenterForOpenScience/SHARE/blob/master/providers/org.escholarship.md
"""

from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class UCeScholarshipHarvester(OAIHarvester):
    short_name = 'ucescholarship'
    long_name = 'eScholarship @ University of California'
    url = 'http://www.escholarship.org/'

    base_url = 'http://www.escholarship.org/uc/oai'
    property_list = [
        'type', 'format', 'date',
        'identifier', 'setSpec', 'source', 'coverage',
        'relation', 'rights'
    ]
