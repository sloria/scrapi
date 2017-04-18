'''
Harvester for the NIST MaterialsData for the SHARE project

Example API call: https://materialsdata.nist.gov/dspace/oai/request?verb=ListRecords&metadataPrefix=oai_dc
'''
from __future__ import unicode_literals

from scrapi.base import OAIHarvester
<<<<<<< HEAD
=======
from scrapi.base.helpers import updated_schema
>>>>>>> 2648529... Fixed Python formatting errors from previous commit


class NistHarvester(OAIHarvester):
    short_name = 'nist'
    long_name = 'NIST MaterialsData'
    url = 'https://materialsdata.nist.gov'
    base_url = 'https://materialsdata.nist.gov/dspace/oai/request'
    property_list = ['relation', 'rights', 'identifier', 'type', 'date', 'setSpec']
    timezone_granularity = True
<<<<<<< HEAD
=======

    @property
    def schema(self):
        return updated_schema(self._schema, {'subjects': ('//dc:subject/node()', format_tags)})


def format_tags(all_tags):
    tags = []
    for tag in all_tags:
        tag = tag.replace("Computational File Repository Categories", '')
        tag = tag.replace("Computational File Repository", '')
        tag = tag.replace("File Repository Categories", '')

        if "::" in tag:
            tags.extend(tag.split("::"))
        if "," in tag:
            tags.extend(tag.split(","))
        elif "::" not in tag:
            tags.append(tag)

    for tag in tags:
        if "::" in tag:
            tags.remove(tag)
        if tag == "":
            tags.remove(tag)
    return tags
>>>>>>> 2648529... Fixed Python formatting errors from previous commit
