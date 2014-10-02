from __future__ import unicode_literals

import json
from copy import deepcopy

import requests

from scrapi import settings


POST_HEADERS = {
    'Content-Type': 'application/json'
}


def create_resource(normalized, hashlist):
    bundle = {
        'systemData': {
            'isProject': True
        },
        'permissions': ['read']
    }

    return _create_node(normalized, bundle, hashlist)['id']


def update_resource(normalized, resource):
    current = _get_metadata(resource)
    # TODO Remove information that would not be included on project ie source
    # and service IDs
    if not is_claimed(resource):
        pass

    # TODO Update actual osf project if unclaimed
    if current['collisionCategory'] > normalized['collisionCategory']:
        new = deepcopy(current.attributes)
        new.update(normalized)
    else:
        new = deepcopy(normalized.attributes)
        new.update(current)

    return _post_metadata(resource, new)


def create_report(normalized, parent, hashlist):
    bundle = {
        'title': '{}: {}'.format(normalized['source'], normalized['title']),
        'parent': parent,
        'category': 'report',
    }

    return _create_node(normalized, bundle, hashlist)['id']


def update_report(normalized, report):
    current = _get_metadata(report)

    if current['collisionCategory'] > normalized['collisionCategory']:
        new = current.attributes
        new.update(normalized)
    else:
        new = normalized.attributes
        new.update(current)

    return _post_metadata(report, new)


def is_event(normalized): # "is event" means "is not project"
    if not normalized.get('contributors'):  # if no contributors, return true
        return True
    if normalized.get('title') == '':  # if there's no title, return true
        return True
    # if it's a type we don't want to be a project, return true
    if normalized['properties'].get('type') is not None:
        dctype = normalized['properties']['type'].lower()
        if dctype is 'letter':
            return True
        if dctype is 'image':
            return True
    return False


def create_event(normalized):
    pass


def is_claimed(resource):
    pass


def get_collision_cat(source):
    return settings.MANIFESTS[source]['collisionCategory']


def clean_report(normalized):
    new = deepcopy(normalized)
    del new['source']
    del new['id']
    return new


def _create_node(normalized, additional, hashlist):
    contributors = [
        {
            'name': '{given} {middle} {family}'.format(**x),
            'email': x.get('email')
        }
        for x in normalized['contributors']
    ]

    bundle = {
        'title': normalized['title'],
        'description': normalized.get('description'),
        'contributors': contributors,
        'tags': normalized.get('tags'),
        'metadata': deepcopy(normalized.attributes),
    }

    bundle.update(additional)

    bundle['metadata']['uuid'] = hashlist

    kwargs = {
        'auth': settings.OSF_AUTH,
        'data': json.dumps(bundle),
        'headers': POST_HEADERS
    }
    return requests.post(settings.OSF_NEW_PROJECT, **kwargs).json()


def _get_metadata(id):
    url = '{}{}/'.format(settings.OSF_APP_URL, id)
    return requests.get(url, auth=settings.OSF_AUTH).json()


def _post_metadata(id, data):
    kwargs = {
        'data': json.dumps(data),
        'headers': POST_HEADERS,
        'auth': settings.OSF_AUTH
    }
    url = '{}{}/'.format(settings.OSF_APP_URL, id)

    requests.post(url, **kwargs)
