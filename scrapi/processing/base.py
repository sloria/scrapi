class BaseProcessor(object):
    NAME = None

    def process_raw(self, raw_doc, **kwargs):
        pass  # pragma: no cover

    def process_normalized(self, raw_doc, normalized, **kwargs):
        pass  # pragma: no cover

    def process_response(self, response):
        pass  # pragma: no cover

    def get_response(self, url=None, method=None):
        pass  # pragma: no cover
