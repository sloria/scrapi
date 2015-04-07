import logging

import requests
from celery import Celery

from scrapi import util
from scrapi import events
from scrapi import database
from scrapi import settings
from scrapi import registry
from scrapi import storage
from scrapi.util import timestamp


app = Celery()
app.config_from_object(settings)

database.setup()
logger = logging.getLogger(__name__)


@app.task
@events.creates_task(events.HARVESTER_RUN)
def run_harvester(harvester_name, days_back=1):
    logger.info('Running harvester "{}"'.format(harvester_name))

    normalization = begin_normalization.s(harvester_name)
    start_harvest = harvest.si(harvester_name, timestamp(), days_back=days_back)

    # Form and start a celery chain
    (start_harvest | normalization).apply_async()


@app.task
@events.logged(events.HARVESTER_RUN)
def harvest(harvester_name, job_created, days_back=1):
    harvest_started = timestamp()
    harvester = registry[harvester_name]

    logger.info('Harvester "{}" has begun harvesting'.format(harvester_name))

    result = harvester.harvest(days_back=days_back)

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
    storage.process_raw(raw_doc, kwargs)


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


@app.task
@events.logged(events.PROCESSING, 'normalized')
def process_normalized(normalized_doc, raw_doc, **kwargs):
    if not normalized_doc:
        raise events.Skip('Not storage document with id {}'.format(raw_doc['docID']))
    storage.process_normalized(raw_doc, normalized_doc, kwargs)


@app.task
def update_pubsubhubbub():
    payload = {'hub.mode': 'publish', 'hub.url': '{url}rss/'.format(url=settings.OSF_APP_URL)}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post('https://pubsubhubbub.appspot.com', headers=headers, params=payload)
