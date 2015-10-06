from datetime import datetime

import os
import re
import six
import pytz
import time
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")
from api.webview.models import Document
logger = logging.getLogger()

URL_RE = re.compile(r'(https?:\/\/[^\/]*)')


xrange = six.moves.xrange


def timestamp():
    return pytz.utc.localize(datetime.utcnow()).isoformat()


def copy_to_unicode(element):
    """ used to transform the lxml version of unicode to a
    standard version of unicode that can be pickalable -
    necessary for linting """

    if isinstance(element, dict):
        return {
            key: copy_to_unicode(val)
            for key, val in element.items()
        }
    elif isinstance(element, list):
        return list(map(copy_to_unicode, element))
    else:
        try:
            # A dirty way to convert to unicode in python 2 + 3.3+
            return u''.join(element)
        except TypeError:
            return element


def stamp_from_raw(raw_doc, **kwargs):
    kwargs['normalizeFinished'] = timestamp()
    stamps = raw_doc['timestamps']
    stamps.update(kwargs)
    return stamps


def format_date_with_slashes(date):
    return date.strftime('%m/%d/%Y')


def json_without_bytes(jobj):
    """
        An ugly hack.

        Before we treat a structure as JSON, ensure that bytes are decoded to str.
    """
    # Create a JSON-compatible copy of the attributes for validation
    jobj = jobj.copy()
    for k, v in jobj.items():
        if isinstance(v, six.binary_type):
            jobj[k] = v.decode('utf8')
    return jobj


def gather_contributors(source):
    source_contributors = []
    source_dict = {'source': source}
    for document in Document.objects.filter(source=source):
        if document.normalized:
            docID = document.normalized['shareProperties']['docID']

            for person in document.normalized['contributors']:
                source_contributors.append({'source': source, 'docID': docID, 'contributor': person})

    source_dict['contributors'] = source_contributors
    return source_dict


def parse_urls_into_groups(source):
    source_dict = {'source': source, 'uris': [], 'all_bases': []}
    for document in Document.objects.filter(source=source):
        if document.normalized:
            docID = document.normalized['shareProperties']['docID']

            source_dict = uri_processing(
                document.normalized['uris']['canonicalUri'],
                source,
                docID,
                source_dict,
                'cannonicalUri'
            )

            if document.normalized['uris'].get('providerUris'):
                for uri in document.normalized['uris']['providerUris']:
                    source_dict = uri_processing(uri, source, docID, source_dict, 'providerUris')
            if document.normalized['uris'].get('descriptorUris'):
                for uri in document.normalized['uris']['descriptorUris']:
                    source_dict = uri_processing(uri, source, docID, source_dict, 'descriptorUris')
            if document.normalized['uris'].get('objectUris'):
                for uri in document.normalized['uris']['objectUris']:
                    if uri:
                        if isinstance(uri, list):
                            for element in uri:
                                source_dict = uri_processing(element, source, docID, source_dict, 'objectUris')
                        else:
                            source_dict = uri_processing(uri, source, docID, source_dict, 'objectUris')

    return source_dict


def uri_processing(uri, source, docID, source_dict, uritype):
    base_uri = URL_RE.search(uri).group()

    if base_uri in source_dict['all_bases']:
        for entry in source_dict['uris']:
            if base_uri == entry['base_uri']:
                entry['individual_uris'].append({
                    'uri': uri,
                    'source': source,
                    'docID': docID,
                    'uritype': uritype
                })
    else:
        source_dict['uris'].append({
            'base_uri': base_uri,
            'individual_uris': [{
                'uri': uri,
                'source': source,
                'docID': docID,
                'uritype': uritype
            }]
        })
        source_dict['all_bases'].append(base_uri)

    return source_dict


def try_n_times(n, action, *args, **kwargs):
    for _ in xrange(n):
        try:
            return action(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            time.sleep(15)
    if e:
        raise e
