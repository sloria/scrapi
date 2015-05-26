import time
import logging

from cassandra.cqlengine.query import Token

from scrapi.database import _manager
from scrapi.processing.cassandra import DocumentModel, DocumentModelV2

_manager.setup()
logger = logging.getLogger(__name__)


def ModelIteratorFactory(model):
    def model_iterator(*sources):
        count = 0
        q = model.objects.timeout(500).allow_filtering().all().limit(1000)
        querysets = (q.filter(source=source) for source in sources) if sources else [q]
        for query in querysets:
            page = try_forever(list, query)
            while len(page) > 0:
                for doc in page:
                    count += 1
                    yield doc
                page = try_forever(next_page, query, page)
    return model_iterator

documents_v1 = ModelIteratorFactory(DocumentModel)
documents = ModelIteratorFactory(DocumentModelV2)


def next_page(query, page):
    return list(query.filter(docID__gt=page[-1].docID))


def try_forever(action, *args, **kwargs):
    while True:
        try:
            return action(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            time.sleep(5)
            logger.info("Trying again...")
