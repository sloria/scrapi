from __future__ import unicode_literals

from .helpers import (
    compose,
    format_tags,
    single_result,
    language_codes,
    datetime_formatter,
    oai_process_uris,
    build_properties,
    oai_process_contributors,
    doe_process_contributors,
)


DOESCHEMA = {
    "description": ('//dc:description/node()', compose(lambda x: x.strip(), single_result)),
    "contributors": ('//dc:creator/node()', compose(doe_process_contributors, lambda x: x.split(';'), single_result)),
    "title": ('//dc:title/node()', compose(lambda x: x.strip(), single_result)),
    "providerUpdatedDateTime": ('//dc:dateEntry/node()', compose(datetime_formatter, single_result)),
    "uris": {
        "canonicalUri": ('//dcq:identifier-citation/node()', compose(lambda x: x.strip(), single_result)),
        "objectUris": [('//dc:doi/node()', compose(lambda x: 'http://dx.doi.org/' + x, single_result))]
    },
    "languages": ("//dc:language/text()", language_codes),
    "publisher": {
        "name": ("//dcq:publisher/node()", single_result)
    },
    "sponsorships": [{
        "sponsor": {
            "sponsorName": ("//dcq:publisherSponsor/node()", single_result)
        }
    }],
    "otherProperties": build_properties(
        ('coverage', '//dc:coverage/node()'),
        ('date', '//dc:date/node()'),
        ('format', '//dc:format/node()'),
        ('identifier', '//dc:identifier/node()'),
        ('identifierDOEcontract', '//dcq:identifierDOEcontract/node()'),
        ('identifierOther', '//dc:identifierOther/node()'),
        ('identifier-purl', '//dc:identifier-purl/node()'),
        ('identifierReport', '//dc:identifierReport/node()'),
        ('publisherAvailability', '//dcq:publisherAvailability/node()'),
        ('publisherCountry', '//dcq:publisherCountry/node()'),
        ('publisherResearch', '//dcq:publisherResearch/node()'),
        ('relation', '//dc:relation/node()'),
        ('rights', '//dc:rights/node()'),
        ('type', '//dc:type/node()'),
        ('typeQualifier', '//dc:typeQualifier/node()')
    )
}

OAISCHEMA = {
    "contributors": ('//dc:creator/node()', '//dc:contributor/node()', oai_process_contributors),
    "uris": ('//dc:doi/node()', '//dc:identifier/node()', oai_process_uris),
    'providerUpdatedDateTime': ('//ns0:header/ns0:datestamp/node()', compose(datetime_formatter, single_result)),
    'title': ('//dc:title/node()', single_result),
    'description': ('//dc:description/node()', single_result),
    'subjects': ('//dc:subject/node()', format_tags),
    'publisher': {
        'name': ('//dc:publisher/node()', single_result)
    },
    'languages': ('//dc:language/text()', language_codes)
}
