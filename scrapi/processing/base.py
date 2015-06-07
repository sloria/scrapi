import abc
from six import add_metaclass


@add_metaclass(abc.ABCMeta)
class BaseProcessor(object):

    NAME = None

    @abc.abstractproperty
    def NAME(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def delete(source, docID):
        pass  # pragma: no cover

    def process_raw(self, raw_doc, **kwargs):
        pass  # pragma: no cover

    def process_normalized(self, raw_doc, normalized, **kwargs):
        pass  # pragma: no cover

    def process_response(self, response):
        pass  # pragma: no cover

    def get_response(self, url=None, method=None):
        pass  # pragma: no cover


@add_metaclass(abc.ABCMeta)
class CanonicalBackend(object):

    @abc.abstractmethod
    def get_raw(source, docID):
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_normalized(source, docID):
        pass  # pragma: no cover

    @abc.abstractmethod
    def iter_raws(source=None):
        pass  # pragma: no cover
