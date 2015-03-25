from __future__ import unicode_literals

import logging
import inspect
from functools import wraps

from fluent import event

from raven import Client

from scrapi import settings


logger = logging.getLogger(__name__)
sentry = Client(dsn=settings.SENTRY_DSN)

if not settings.USE_FLUENTD:
    logger.warning('USE_FLUENTD is set to False; logs will not be stored')

# Events
PROCESSING = 'storage'
HARVESTER_RUN = 'runHarvester'
CHECK_ARCHIVE = 'checkArchive'
NORMALIZATION = 'normalization'

# statuses
FAILED = 'failed'
SKIPPED = 'skipped'
CREATED = 'created'
STARTED = 'started'
COMPLETED = 'completed'


def log_to_sentry(message, **kwargs):
    if not settings.SENTRY_DSN:
        return logger.warn('send_to_raven called with no SENTRY_DSN')
    return sentry.captureMessage(message, extra=kwargs)


class Skip(Exception):
    pass


def serialize_fluent_data(data):
    if isinstance(data, dict):
        return {
            key: serialize_fluent_data(val)
            for key, val in data.items()
        }
    elif isinstance(data, list):
        return [
            serialize_fluent_data(item)
            for item in data
        ]
    elif isinstance(data, (str, unicode)):
        return data
    else:
        return repr(data)


# Ues _index here as to not clutter the namespace for kwargs
def dispatch(_event, status, _index=None, **kwargs):
    if not settings.USE_FLUENTD:
        return

    evnt = {
        'event': _event,
        'status': status
    }

    evnt.update(serialize_fluent_data(kwargs))

    if _index:
        _event = '{}.{}'.format(_event, _index)

    logger.debug('[{}][{}]{!r}'.format(_event, status, kwargs))
    event.Event(_event, evnt)


def logged(event, index=None):
    def _logged(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            context = extract_context(func, *args, **kwargs)
            dispatch(event, STARTED, _index=index, **context)
            try:
                res = func(*args, **kwargs)
            except Skip as e:
                dispatch(event, SKIPPED, _index=index, reason=e.message, **context)
                return None
            except Exception as e:
                dispatch(event, FAILED, _index=index, exception=e, **context)
                raise
            else:
                dispatch(event, COMPLETED, _index=index, **context)
            return res
        return wrapped
    return _logged


def extract_context(func, *args, **kwargs):
    args = list(reversed(args))
    arginfo = inspect.getargspec(func)

    if arginfo.defaults:
        arg_names = arginfo.args[:len(arginfo.defaults)]
        kwarg_names = arginfo.args[len(arginfo.defaults):]
    else:
        kwarg_names = []
        arg_names = arginfo.args

    real_args = {
        key: kwargs.pop(key, val)
        for key, val
        in zip(kwarg_names, arginfo.defaults or [])
    }

    for name in arg_names:
        real_args[name] = args.pop()

    if arginfo.varargs:
        real_args[arginfo.varargs] = list(reversed(args))

    if arginfo.keywords:
        real_args[arginfo.keywords] = kwargs

    return real_args


def creates_task(event):
    def _creates_task(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            res = func(*args, **kwargs)
            dispatch(event, CREATED, **extract_context(func, *args, **kwargs))
            return res
        return wrapped
    return _creates_task
