"""A wrapper around requests that records all requests made with it.
    Supports get, put, post, delete and request
    all calls return an instance of HarvesterResponse
"""
from __future__ import absolute_import

import json
import time
import logging
import functools
from datetime import datetime

import furl
import requests
import cqlengine
from cqlengine import columns
from requests.structures import CaseInsensitiveDict

from scrapi import events
from scrapi import database
from scrapi import settings

logger = logging.getLogger(__name__)
logging.getLogger('cqlengine.cql').setLevel(logging.WARN)


@database.register_model
class HarvesterResponse(cqlengine.Model):
    __table_name__ = 'responses'

    method = columns.Text(primary_key=True)
    url = columns.Text(primary_key=True, required=True)

    # Raw request data
    ok = columns.Boolean()
    content = columns.Bytes()
    encoding = columns.Text()
    headers_str = columns.Text()
    status_code = columns.Integer()
    time_made = columns.DateTime(default=datetime.now)

    def json(self):
        return json.loads(self.content)

    @property
    def headers(self):
        return CaseInsensitiveDict(json.loads(self.headers_str))

    @property
    def text(self):
        return self.content.decode('utf-8')


def _maybe_load_response(method, url):
    try:
        return HarvesterResponse.get(url=url, method=method)
    except HarvesterResponse.DoesNotExist:
        return None


def record_or_load_response(method, url, throttle=None, force=False, params=None, **kwargs):
    if params:
        url = furl.furl(url).set(args=params).url

    resp = _maybe_load_response(method, url)

    if not force and resp and resp.ok:
        logger.info('Return recorded response from "{}"'.format(url))
        return resp

    if force:
        logger.warning('Force updating request to "{}"'.format(url))
    else:
        logger.info('Making request to "{}"'.format(url))

    if throttle:
        time.sleep(throttle)

    response = requests.request(method, url, **kwargs)

    if not response.ok:
        events.log_to_sentry('Got non-ok response code.', url=url, method=method)

    if not resp:
        return HarvesterResponse(
            url=url,
            method=method,
            ok=response.ok,
            content=response.content,
            encoding=response.encoding,
            status_code=response.status_code,
            headers_str=json.dumps(dict(response.headers))
        ).save()

    logger.warning('Skipped recorded response from "{}"'.format(url))

    return resp.update(
        ok=response.ok,
        content=response.content,
        encoding=response.encoding,
        status_code=response.status_code,
        headers_str=json.dumps(dict(response.headers))
    ).save()


def request(method, url, **kwargs):
    """Make a recorded request or get a record matching method and url
    :param str method: Get, Put, Post, or Delete
    :param str url: Where to make the request to
    :param bool force: Whether or not to force the new request to be made
    :param int throttle: A time in seconds to sleep before making requests
    :param dict kwargs: Addition keywords to pass to requests
    """
    if settings.RECORD_HTTP_TRANSACTIONS:
        return record_or_load_response(method, url, **kwargs)

    logger.info('Making request to "{}"'.format(url))
    return requests.request(method, url, **kwargs)


get = functools.partial(request, 'get')
put = functools.partial(request, 'put')
post = functools.partial(request, 'post')
delete = functools.partial(request, 'delete')
