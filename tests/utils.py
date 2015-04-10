from __future__ import unicode_literals

from scrapi.base.helpers import updated_schema
from scrapi.base.schemas import BASEXMLSCHEMA

RAW_DOC = {
    'doc': str('{}'),
    'docID': 'someID',
    'timestamps': {
        'harvestFinished': '2012-11-30T17:05:48+00:00',
        'harvestStarted': '2012-11-30T17:05:48+00:00',
        'harvestTaskCreated': '2012-11-30T17:05:48+00:00'
    },
    'filetype': 'json',
    'source': 'crossref'
}

NORMALIZED_DOC = {
    'title': 'No',
    'contributors': [{'name': ''}],
    'source': 'crossref',
    'providerUpdatedDateTime': '2014-04-04T00:00:00',
    'uris': {
        'canonicalUri': 'http://example.com/direct'
    }
}

RECORD = {
    'title': 'Using Table Stable Carbon in Gold and STAR Isotopes',
    'contributors': [
        {
            'name': 'DEVON Get The Tables DUDLEY',
            'givenName': 'DEVON',
            'additionalName': 'Get The Tables',
            'familyName': 'DUDLEY',
            'email': 'dudley.boyz@email.uni.edu',
            'sameAs': ['http://example.com/me']
        }
    ],
    'uris': {
        'canonicalUri': 'http://www.plosone.org/article'
    },
    # 'otherProperties': {
    #     'figures': ['http://www.plosone.org/article/image.png'],
    #     'type': 'text',
    #             'yep': 'A property'
    # },
    'description': 'This study seeks to understand how humans impact\
            the dietary patterns of eight free-ranging vervet monkey\
            (Chlorocebus pygerythrus) groups in South Africa using stable\
            isotope analysis.',
    'providerUpdatedDateTime': '2015-02-23T00:00:00',
    'shareProperties': {
        'source': 'crossref'
    }
}


TEST_SCHEMA = updated_schema(BASEXMLSCHEMA, {
    "title": ("//dc:title/node()", lambda x: "Title overwritten"),
    # "otherProperties": {
    #     "title1": "//dc:title/node()",
    #     "title2": ["//dc:title/node()", lambda x: x.lower()],
    #     "title3": ["//dc:title/node()", "//dc:title/node()", lambda x, y: x + y.lower()]
    # }
})


def get_leaves(d, leaves=None):
    if leaves is None:
        leaves = []

    for k, v in d.items():
        if isinstance(v, dict):
            leaves.extend(get_leaves(v, leaves))
        else:
            leaves.append((k, v))

    return leaves


TEST_NAMESPACES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcq': 'http://purl.org/dc/terms/'
}


TEST_XML_DOC = '''
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcq="http://purl.org/dc/terms/">
        <records count="97" morepages="true" start="1" end="10">
            <record rownumber="1">
                <dc:title>Test</dc:title>
                <dc:creator>
                Raveh-Sadka, Tali; Thomas, Brian C; Singh, Andrea; Firek, Brian; Brooks,
                Brandon; Castelle, Cindy J; Sharon, Itai; Baker, Robyn; Good, Misty; Morowitz,
                Michael J; Banfield, Jillian F
                </dc:creator>
                <dc:subject/>
                <dc:subjectRelated/>
                <dc:description/>
                <dcq:publisher>
                    eLife Sciences Publications, Ltd.
                </dcq:publisher>
                <dcq:publisherAvailability/>
                <dcq:publisherResearch>
                    None
                </dcq:publisherResearch>
                <dcq:publisherSponsor>
                    USDOE
                </dcq:publisherSponsor>
                <dcq:publisherCountry>
                    Country unknown/Code not available
                </dcq:publisherCountry>
                <dc:date>
                    2015-03-03
                </dc:date>
                <dc:language>
                    English
                </dc:language>
                <dc:type>
                    Journal Article
                </dc:type>
                <dcq:typeQualifier/>
                <dc:relation>
                    Journal Name: eLife; Journal Volume: 4
                </dc:relation>
                <dc:coverage/>
                <dc:format>
                    Medium: X
                </dc:format>
                <dc:identifier>
                    OSTI ID: 1171761, Legacy ID: OSTI ID: 1171761
                </dc:identifier>
                <dc:identifierReport>
                    None
                </dc:identifierReport>
                <dcq:identifierDOEcontract>
                    5R01AI092531; Long term fellowship; SC0004918; ER65561; APSF-2012-10-05
                </dcq:identifierDOEcontract>
                <dc:identifierOther>Journal ID: ISSN 2050-084X</dc:identifierOther>
                <dc:doi>10.7554/eLife.05477</dc:doi><dc:rights/>
                <dc:dateEntry>2015-03-05</dc:dateEntry>
                <dc:dateAdded>2015-03-05</dc:dateAdded>
                <dc:ostiId>1171761</dc:ostiId>
                <dcq:identifier-purl type=""/>
                <dcq:identifier-citation>
                    http://www.osti.gov/pages/biblio/1171761
                </dcq:identifier-citation>
            </record>
        </records>
    </rdf:RDF>
'''

TEST_OAI_DOC = '''
    <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <responseDate>2015-03-30T18:31:29Z</responseDate>
    <request verb="ListRecords" metadataPrefix="oai_dc" from="2014-09-26T00:00:00Z">http://repository.stcloudstate.edu/do/oai/</request>
    <ListRecords>
    <record>
    <header>
    <identifier>oai:digitalcommons.calpoly.edu:aged_rpt-1085</identifier>
    <datestamp>2014-10-07T00:30:57Z</datestamp>
    <setSpec>publication:aged_rpt</setSpec>
    <setSpec>publication:students</setSpec>
    </header>
    <metadata>
    <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
    <dc:title>Test</dc:title>
    <dc:creator>Mills, Donald W, Jr.</dc:creator>
    <dc:description>
    This internship report consists of two parts. The first section addresses the Quality Criteria in Agricultural Education for the program of agricultural instruction at Arvin High School. The second section explains the steps in remodeling the agriculture classroom and agriculture mechanics shop at Arvin High School. The remodeling of the facility was accomplished to address the occupational needs for students entering the work force immediately after high school. It was also designed to prepare students for opportunities in higher education.
    </dc:description>
    <dc:date>2014-05-01T07:00:00Z</dc:date>
    <dc:type>text</dc:type>
    <dc:format>application/pdf</dc:format>
    <dc:identifier>http://digitalcommons.calpoly.edu/aged_rpt/64</dc:identifier>
    <dc:identifier>
    http://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=1085&amp;context=aged_rpt
    </dc:identifier>
    <dc:source>
    Graduate Internship Reports in Agricultural Education
    </dc:source>
    <dc:publisher>DigitalCommons@CalPoly</dc:publisher>
    </oai_dc:dc>
    </metadata>
    </record>
    </ListRecords>
    </OAI-PMH>
'''
