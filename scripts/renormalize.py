import time
import logging

from cqlengine import Token

from scrapi.database import _manager
from scrapi.processing.cassandra import DocumentModel
from scrapi.processing.elasticsearch import es
from scrapi.tasks import normalize, process_normalized
from scrapi.linter import RawDocument


ROW_LIMIT = 10000
_manager.setup()
logger = logging.getLogger(__name__)


def document_generator():
    count = 0
    query = DocumentModel.objects.all().limit(ROW_LIMIT)
    page = query
    while len(page) > 0:
        for doc in page:
            count += 1
            if es.exists(index='share_v1', doc_type=doc.source, id=doc.docID) and doc.doc and doc.docID:
                try:
                    if not doc.docID or not doc.doc:
                        continue
                    yield RawDocument({
                        'doc': doc.doc,
                        'docID': doc.docID,
                        'source': doc.source,
                        'filetype': doc.filetype,
                        'timestamps': doc.timestamps
                    })
                except Exception as e:
                    logger.exception(e)
        tick = time.time()
        page = query.filter(pk__token__gt=Token(page[-1].pk))
        logger.info('Time to query {} documents: {}'.format(ROW_LIMIT, time.time() - tick))
        logger.info('{} documents iterated'.format(count))


def main():
    for raw in document_generator():
        try:
            process_normalized.delay(normalize(raw, raw['source']), raw)
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    main()
