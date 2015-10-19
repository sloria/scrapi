import ast
import logging
import requests
from lxml import etree
from datetime import date, timedelta
from requests.auth import HTTPBasicAuth

from api.api import settings


NAMESPACES = {'dc': 'http://purl.org/dc/elements/1.1/',
              'oai_dc': 'http://www.openarchives.org/OAI/2.0/',
              'ns0': 'http://www.openarchives.org/OAI/2.0/'}
BASE_SCHEMA = ['title', 'contributor', 'creator', 'subject', 'description']

logger = logging.getLogger(__name__)


def format_set_choices(pre_saved_data):

    sets = pre_saved_data.approved_sets
    sets = ast.literal_eval(sets)
    approved_set_set = set((item[0].replace('publication:', ''), item[1]) for item in sets)

    return approved_set_set


def get_session_item(request, item):
    return request.session[item]


def get_oai_properties(base_url):
    """ Makes 2 requests to the provided base URL:
        1 for the sets available
        1 for the list of properties

        returns a dict with list of properties, and set_groups.

        Set groups is a list of tuples - first element is short name,
        second element is the long descriptive name.

        The sets available are added as multiple selections for the next form,
        the properties are pre-loaded into the properties field.
    """
    try:
        # request 1 for the setSpecs available
        set_url = base_url.strip() + '?verb=ListSets'
        set_data_request = requests.get(set_url)
        all_content = etree.XML(set_data_request.content)

        all_sets = all_content.xpath('//oai_dc:set', namespaces=NAMESPACES)
        all_set_info = [one.getchildren() for one in all_sets]

        set_groups = []
        for item in all_set_info:
            one_group = (item[0].text, item[1].text)
            set_groups.append(one_group)

        # request 2 for records 30 days back just in case
        start_date = str(date.today() - timedelta(30))
        prop_url = base_url + '?verb=ListRecords&metadataPrefix=oai_dc&from={}T00:00:00Z'.format(start_date)
        prop_data_request = requests.get(prop_url)
        all_prop_content = etree.XML(prop_data_request.content)
        try:
            pre_names = all_prop_content.xpath('//ns0:metadata', namespaces=NAMESPACES)[0].getchildren()[0].getchildren()
        except IndexError:
            prop_url = base_url + '?verb=ListRecords&metadataPrefix=oai_dc&from={}'.format(start_date)
            prop_data_request = requests.get(prop_url)
            all_prop_content = etree.XML(prop_data_request.content)
            pre_names = all_prop_content.xpath('//ns0:metadata', namespaces=NAMESPACES)[0].getchildren()[0].getchildren()

        all_names = [name.tag.replace('{' + NAMESPACES['dc'] + '}', '') for name in pre_names]
        property_names = list({name for name in all_names if name not in BASE_SCHEMA})

        return {'properties': property_names, 'sets': set_groups}

    # If anything at all goes wrong, just render a blank form...
    except Exception as e:
        logger.info(e)
        raise ValueError('OAI Processing Error - {}'.format(e))


def compose_desk_email(reg_type, name, email):
    if reg_type == 'incomplete':
        body = 'Hello {},\n\nThank you for beginning to register a provider to participate in the beta of SHARE Notify! We see that you have started the registration process, but have not yet completed it, perhaps due to potential metadata license restrictions for your provider.'.format(name)

        subject = 'SHARE registration follow-up'
    else:
        subject = 'SHARE - registration confirmation'

        body = '''Hello {},

Thank you for registering a provider to participate in the Beta release of SHARE Notify! We will evaluate your provider based on the information you have provided, and will get back to you soon soon with any questions we may have.
'''.format(name)

    body += '''Please let us know if you have any questions about the process. As SHARE Notify is currently in beta, we would also appreciate any feedback or insights about the provider registration process.  Subscribe to the SHARE email list to stay updated with ongoing progress (see form at the bottom of this page: http://www.share-research.org/).

Sincerely,
{}'''.format(settings.EMAIL_SIGNATURE)

    message = {
        "type": "email",
        "subject": subject,
        "priority": 4,
        "status": "open",
        "labels": ["Spam", "Ignore"],
        "message": {
            "direction": "out",
            "body": body,
            "to": email,
            "from": settings.FROM_EMAIL,
            "subject": "My email subject"
        },
        "_links": {
            "customer": {
                "class": "customer",
                "href": "/api/v2/customers/1"
            },
            "assigned_group": {
                "href": "/api/v2/groups/1",
                "class": "group"
            }
        }
    }

    requests.post(
        'http://openscience.desk.com/',
        auth=HTTPBasicAuth(settings.DESK_EMAIL, settings.DESK_PASSWORD),
        json=message
    )
