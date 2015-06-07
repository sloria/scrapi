"""A wrapper around requests that records all requests made with it.
    Supports get, put, post, delete and request
    all calls return an instance of HarvesterResponse
"""
from __future__ import absolute_import

import json
import time
import logging
import functools

import furl
import requests
from requests.structures import CaseInsensitiveDict

from scrapi import events
from scrapi import settings
from scrapi.processing import process_response, get_response

logger = logging.getLogger(__name__)
logging.getLogger('cqlengine.cql').setLevel(logging.WARN)


class HarvesterResponse(object):
    """A parody of requests.response but stored in cassandra
    Should reflect all methods of a response object
    Contains an additional field time_made, self-explanitory
    """

    class DoesNotExist(Exception):
        pass

    def __init__(self, method=None, url=None, ok=None, content=None, encoding=None, headers_str=None, status_code=None, time_made=None):
        if not method or not url:
            pass  # TODO
        self.method = method
        self.url = url
        self.ok = ok
        self.content = content
        self.encoding = encoding
        self.headers_str = headers_str
        self.status_code = status_code
        self.time_made = time_made

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield k, v

    def save(self):
        process_response(self)
        return self

    @classmethod
    def get(cls, url=None, method=None):
        """
            Returns a list of matching responses
            if multiple response backends are enabled,
            will return the first one  # TODO
        """
        try:
            responses = get_response(url=url, method=method)
        except Exception:  # TODO
            responses = []
        if not responses:
            raise cls.DoesNotExist
        return cls(**dict(responses[0]))

    def update(self, **kwargs):
        self.__dict__.update(**kwargs)
        return self

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


def record_or_load_response(method, url, throttle=None, force=False, params=None, expected=(200,), **kwargs):

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
        ok=(response.ok or response.status_code in expected),
        content=response.content,
        encoding=response.encoding,
        status_code=response.status_code,
        headers_str=json.dumps(dict(response.headers))
    ).save()


def request(method, url, params=None, **kwargs):
    """Make a recorded request or get a record matching method and url

    :param str method: Get, Put, Post, or Delete
    :param str url: Where to make the request to
    :param bool force: Whether or not to force the new request to be made
    :param int throttle: A time in seconds to sleep before making requests
    :param dict kwargs: Addition keywords to pass to requests
    """
    if params:
        url = furl.furl(url).set(args=params).url
    logger.info(url)
    if settings.RECORD_HTTP_TRANSACTIONS:
        return record_or_load_response(method, url, **kwargs)

    logger.info('Making request to "{}"'.format(url))
    time.sleep(kwargs.pop('throttle', 0))
    return requests.request(method, url, **kwargs)


get = functools.partial(request, 'get')
put = functools.partial(request, 'put')
post = functools.partial(request, 'post')
delete = functools.partial(request, 'delete')
