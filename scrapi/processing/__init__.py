import os

from scrapi import settings
from scrapi.processing.base import BaseProcessor, CanonicalBackend

__all__ = []
for mod in os.listdir(os.path.dirname(__file__)):
    root, ext = os.path.splitext(mod)
    if ext == '.py' and root not in ['__init__', 'base']:
        __all__.append(root)

from . import *


def get_processor(processor_name):
    for klass in BaseProcessor.__subclasses__():
        if klass.NAME == processor_name:
            return klass()
    raise NotImplementedError('No Processor {}'.format(processor_name))

raw_processors = map(get_processor, settings.RAW_PROCESSING)
normalized_processors = map(get_processor, settings.NORMALIZED_PROCESSING)
response_processors = map(get_processor, settings.NORMALIZED_PROCESSING)
canonical_backend = filter(lambda x: isinstance(x, CanonicalBackend), raw_processors)[0]


def process_normalized(raw_doc, normalized, kwargs):
    ''' kwargs is a dictiorary of kwargs.
        keyed by the processor name
        Exists so that when we run check archive we
        specifiy that it's ok to overrite certain files
    '''
    for p in normalized_processors:
        extras = kwargs.get(p, {})
        p.process_normalized(raw_doc, normalized, **extras)


def process_raw(raw_doc, kwargs):
    for p in raw_processors:
        extras = kwargs.get(p, {})
        p.process_raw(raw_doc, **extras)


def process_response(response):
    for p in response_processors:
        p.process_response(response)


def get_response(url=None, method=None):
    return [p.get_response(url=url, method=method) for p in response_processors]


def delete(source, docID):
    for p in set(raw_processors + normalized_processors):
        p.delete(source, docID)


def get_raw(source, docID):
    return canonical_backend.get_raw(source, docID)


def get_normalized(source, docID):
    return canonical_backend.get_normalized(source, docID)


def iter_raws(source=None):
    return canonical_backend.get_normalized(source)
