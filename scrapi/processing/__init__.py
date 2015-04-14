import os

from scrapi import settings
from scrapi.processing.base import BaseProcessor


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


def process_normalized(raw_doc, normalized, kwargs):
    ''' kwargs is a dictiorary of kwargs.
        keyed by the processor name
        Exists so that when we run check archive we
        specifiy that it's ok to overrite certain files
    '''
    for p in settings.NORMALIZED_PROCESSING:
        extras = kwargs.get(p, {})

        try:
            from scrapi.tasks import process_specific_normalized
            process_specific_normalized.delay(get_processor(p), raw_doc, normalized, **extras)
            # get_processor(p).process_normalized(raw_doc, normalized, **extras)
        except Exception:
            if settings.DEBUG:
                raise
            else:
                logger.exception(e)


def process_raw(raw_doc, kwargs):
    for p in settings.RAW_PROCESSING:
        extras = kwargs.get(p, {})
        try:
            get_processor(p).process_raw(raw_doc, **extras)
        except Exception as e:
            if settings.DEBUG:
                raise
            else:
                logger.exception(e)
