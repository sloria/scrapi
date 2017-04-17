"""
Harvests Virginia Tech VTechWorks metadata for ingestion into the SHARE service

Information about VTechWorks at https://github.com/CenterForOpenScience/SHARE/blob/master/providers/edu.vt.vtechworks.md

Example API call: http://vtechworks.lib.vt.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc&from=2014-09-29
"""

from __future__ import unicode_literals

from scrapi.base import OAIHarvester
from scrapi.base import helpers


def oai_process_uris_vtech(*args):

    identifiers = helpers.gather_identifiers(args)
    provider_uris, object_uris = helpers.seperate_provider_object_uris(identifiers)

    for i, uri in enumerate(provider_uris):
        if 'handle' in uri:
            doc_id = provider_uris[i].replace('http://hdl.handle.net/10919/', '')
            provider_uris[i] = 'http://vtechworks.lib.vt.edu/handle/10919/' + doc_id

    for i, uri in enumerate(object_uris):
        if 'handle' in uri:
            doc_id = object_uris[i].replace('http://hdl.handle.net/10919/', '')
            object_uris[i] = 'http://vtechworks.lib.vt.edu/handle/10919/' + doc_id

    potential_uris = (provider_uris + object_uris)

    try:
        canonical_uri = potential_uris[0]
    except IndexError:
        raise ValueError('No Canonical URI was returned for this record.')

    return {
        'canonicalUri': canonical_uri,
        'objectUris': object_uris,
        'providerUris': provider_uris
    }


class VTechHarvester(OAIHarvester):
    short_name = 'vtech'
    long_name = 'Virginia Tech VTechWorks'
    url = 'https://vtechworks.lib.vt.edu'

    @property
    def schema(self):
        return helpers.updated_schema(self._schema, {
            "uris": ('//ns0:header/ns0:identifier/node()', '//dc:identifier/node()', oai_process_uris_vtech)
        })

    base_url = 'http://vtechworks.lib.vt.edu/oai/request'
    property_list = [
        'type', 'source', 'format', 'date',
        'identifier', 'setSpec', 'rights', 'relation'
    ]
