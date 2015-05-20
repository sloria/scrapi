import logging

from scripts.util import documents

from scrapi.tasks import process_raw, process_normalized
from scrapi.processing.cassandra import as_raw, as_normalized

logger = logging.getLogger(__name__)


def migrate_to_v2():
    count = 0
    exceptions = []
    for doc in documents():
        count += 1
        try:
            raw, normalized = as_raw(doc), as_normalized(doc)
            process_raw(raw)
            process_normalized(normalized, raw)
        except Exception as e:
            logger.exception(e)
            exceptions.append(e)

    for ex in exceptions:
        logger.exception(e)
    logger.info('{} documents processed, with {} exceptions'.format(count, len(exceptions)))

if __name__ == '__main__':
    migrate_to_v2()
