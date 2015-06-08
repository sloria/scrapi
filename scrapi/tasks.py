import logging
import functools
from datetime import date, timedelta

from celery import Celery

from scrapi import util
from scrapi import events
from scrapi import database
from scrapi import settings
from scrapi import registry
from scrapi import processing
from scrapi.util import timestamp

from scripts.util import documents


app = Celery()
app.config_from_object(settings)

database.setup()
logger = logging.getLogger(__name__)


def task_autoretry(*args_task, **kwargs_task):
    def actual_decorator(func):
        @app.task(*args_task, **kwargs_task)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except kwargs_task.get('autoretry_on', Exception) as exc:
                logger.info('Retrying with exception {}'.format(exc))
                wrapper.retry(exc=exc)
        return wrapper
    return actual_decorator


@app.task
@events.creates_task(events.HARVESTER_RUN)
def run_harvester(harvester_name, start_date=None, end_date=None):
    logger.info('Running harvester "{}"'.format(harvester_name))

    start_date = start_date or date.today() - timedelta(settings.DAYS_BACK)
    end_date = end_date or date.today()

    normalization = begin_normalization.s(harvester_name)
    start_harvest = harvest.si(harvester_name, timestamp(), start_date=start_date, end_date=end_date)

    # Form and start a celery chain
    (start_harvest | normalization).apply_async()


@app.task
@events.logged(events.HARVESTER_RUN)
def harvest(harvester_name, job_created, start_date=None, end_date=None):
    harvest_started = timestamp()
    harvester = registry[harvester_name]

    start_date = start_date or date.today() - timedelta(settings.DAYS_BACK)
    end_date = end_date or date.today()

    logger.info('Harvester "{}" has begun harvesting'.format(harvester_name))

    result = harvester.harvest(start_date=start_date, end_date=end_date)

    # result is a list of all of the RawDocuments harvested
    return result, {
        'harvestFinished': timestamp(),
        'harvestTaskCreated': job_created,
        'harvestStarted': harvest_started,
    }


@app.task
def begin_normalization((raw_docs, timestamps), harvester_name):
    '''harvest_ret is harvest return value:
        a tuple contaiing list of rawDocuments and
        a dictionary of timestamps
    '''
    logger.info('Normalizing {} documents for harvester "{}"'
                .format(len(raw_docs), harvester_name))
    # raw is a single raw document
    for raw in raw_docs:
        spawn_tasks(raw, timestamps, harvester_name)


@events.creates_task(events.PROCESSING)
@events.creates_task(events.NORMALIZATION)
def spawn_tasks(raw, timestamps, harvester_name):
    raw['timestamps'] = timestamps
    raw['timestamps']['normalizeTaskCreated'] = timestamp()
    chain = (normalize.si(raw, harvester_name) | process_normalized.s(raw))

    chain.apply_async()
    process_raw.delay(raw)


@app.task
@events.logged(events.PROCESSING, 'raw')
def process_raw(raw_doc, **kwargs):
    processing.process_raw(raw_doc, kwargs)


@app.task
@events.logged(events.NORMALIZATION)
def normalize(raw_doc, harvester_name):
    normalized_started = timestamp()
    harvester = registry[harvester_name]

    normalized = harvester.normalize(raw_doc)

    if not normalized:
        raise events.Skip('Did not normalize document with id {}'.format(raw_doc['docID']))

    normalized['timestamps'] = util.stamp_from_raw(raw_doc, normalizeStarted=normalized_started)

    return normalized  # returns a single normalized document


@app.task(default_retry_delay=30, max_retries=5)
@events.logged(events.PROCESSING, 'normalized')
def process_normalized(normalized_doc, raw_doc, **kwargs):
    try:
        if not normalized_doc:
            raise events.Skip('Not processing document with id {}'.format(raw_doc['docID']))
        processing.process_normalized(raw_doc, normalized_doc, kwargs)
    except Exception as e:
        logger.info('Retrying withiin PROCESS NORMALIZED with exception {}'.format(e))
        process_normalized.retry(exc=e)


@app.task
def migrate(migration, **kwargs):
    count = 0
    for doc in documents(kwargs['source']):
        count += 1

        migration.s(doc, kwargs['source'], kwargs['target'], kwargs.get('dry')).apply_async()

    if kwargs.get('dry'):
        logger.info('Dry run complete')

    logger.info('{} documents processed for migration {}'.format(count, str(migration)))
