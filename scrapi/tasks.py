import logging
import functools
from datetime import date, timedelta

import requests
from celery import Celery

from scrapi import util
from scrapi import events
from scrapi import database
from scrapi import settings
from scrapi import registry
from scrapi import processing
from scrapi.util import timestamp

from scripts.util import documents
from scrapi.linter import RawDocument
from scrapi.processing.elasticsearch import es


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


@task_autoretry(default_retry_delay=30, max_retries=5)
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


@task_autoretry(default_retry_delay=30, max_retries=5)
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


@task_autoretry(default_retry_delay=30, max_retries=5)
@events.logged(events.PROCESSING, 'raw')
def process_raw(raw_doc, **kwargs):
    processing.process_raw(raw_doc, kwargs)


@task_autoretry(default_retry_delay=30, max_retries=5)
@events.logged(events.NORMALIZATION)
def normalize(raw_doc, harvester_name):
    normalized_started = timestamp()
    harvester = registry[harvester_name]

    normalized = harvester.normalize(raw_doc)

    if not normalized:
        raise events.Skip('Did not normalize document with id {}'.format(raw_doc['docID']))

    normalized['timestamps'] = util.stamp_from_raw(raw_doc, normalizeStarted=normalized_started)

    return normalized  # returns a single normalized document


@task_autoretry(default_retry_delay=30, max_retries=5)
@events.logged(events.PROCESSING, 'normalized')
def process_normalized(normalized_doc, raw_doc, **kwargs):
    if not normalized_doc:
        raise events.Skip('Not processing document with id {}'.format(raw_doc['docID']))
    processing.process_normalized(raw_doc, normalized_doc, kwargs)


@task_autoretry(default_retry_delay=30, max_retries=5)
def update_pubsubhubbub():
    payload = {'hub.mode': 'publish', 'hub.url': '{url}rss/'.format(url=settings.OSF_APP_URL)}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post('https://pubsubhubbub.appspot.com', headers=headers, params=payload)


@task_autoretry(default_retry_delay=30, max_retries=5)
def rename(source, target, dry=True):
    assert source != target, "Can't rename {} to {}, names are the same".format(source, target)
    count = 0
    for doc in documents(source):
        count += 1
        rename_one.apply_async((doc, source, target, dry))

    if dry:
        logger.info('Dry run complete')

    logger.info('{} documents processed'.format(count))


@task_autoretry(default_retry_delay=30, max_retries=5)
def rename_one(doc, source, target, dry):
    raw = RawDocument({
        'doc': doc.doc,
        'docID': doc.docID,
        'source': target,
        'filetype': doc.filetype,
        'timestamps': doc.timestamps,
        'versions': doc.versions
    })
    if not dry:
        process_raw(raw)
        process_normalized(normalize(raw, raw['source']), raw)
        logger.info('Processed document from {} with id {}'.format(source, raw['docID']))

        es.delete(index=settings.ELASTIC_INDEX, doc_type=source, id=raw['docID'], ignore=[404])
        es.delete(index='share_v1', doc_type=source, id=raw['docID'], ignore=[404])
    logger.info('Deleted document from {} with id {}'.format(source, raw['docID']))
