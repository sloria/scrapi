import logging

from scripts.util import documents

from scrapi.processing.cassandra import DocumentModelV2

logger = logging.getLogger(__name__)


def migrate_to_v2():
    count = 0
    exceptions = []
    for doc in documents():
        count += 1
        try:
            DocumentModelV2.create(**dict(doc)).save()
        except Exception as e:
            logger.exception(e)
            exceptions.append(e)

    for ex in exceptions:
        logger.exception(e)
    logger.info('{} documents processed, with {} exceptions'.format(count, len(exceptions)))

if __name__ == '__main__':
    migrate_to_v2()
