import logging
import json
import functools
from itertools import islice
from datetime import date, timedelta

from celery import Celery

from scrapi import util
from scrapi import events
from scrapi import database
from scrapi import settings
from scrapi import registry
from scrapi import processing
from scrapi.util import timestamp

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
                return func(*args, **kwargs)
            except kwargs_task.get('autoretry_on', Exception) as exc:
                logger.info('Retrying with exception {}'.format(exc))
                raise wrapper.retry(exc=exc)
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
def begin_normalization(raw_docs_timestamps, harvester_name):
    '''harvest_ret is harvest return value:
        a tuple contaiing list of rawDocuments and
        a dictionary of timestamps
    '''
    (raw_docs, timestamps) = raw_docs_timestamps
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


@task_autoretry(default_retry_delay=settings.CELERY_RETRY_DELAY, max_retries=settings.CELERY_MAX_RETRIES)
@events.logged(events.PROCESSING, 'raw')
def process_raw(raw_doc, **kwargs):
    processing.process_raw(raw_doc, kwargs)


@task_autoretry(default_retry_delay=settings.CELERY_RETRY_DELAY, max_retries=settings.CELERY_MAX_RETRIES, throws=events.Skip)
@events.logged(events.NORMALIZATION)
def normalize(raw_doc, harvester_name):
    normalized_started = timestamp()
    harvester = registry[harvester_name]

    normalized = harvester.normalize(raw_doc)

    if not normalized:
        raise events.Skip('Did not normalize document with id {}'.format(raw_doc['docID']))

    normalized['timestamps'] = util.stamp_from_raw(raw_doc, normalizeStarted=normalized_started)

    return normalized  # returns a single normalized document


@task_autoretry(default_retry_delay=settings.CELERY_RETRY_DELAY, max_retries=settings.CELERY_MAX_RETRIES, throws=events.Skip)
@events.logged(events.PROCESSING, 'normalized')
def process_normalized(normalized_doc, raw_doc, **kwargs):
    if not normalized_doc:
        raise events.Skip('Not processing document with id {}'.format(raw_doc['docID']))
    processing.process_normalized(raw_doc, normalized_doc, kwargs)


@task_autoretry(default_retry_delay=settings.CELERY_RETRY_DELAY, max_retries=0)
@events.logged(events.PROCESSSING_URIS, 'uri_processing')
def process_uris(async, **kwargs):
    settings.CELERY_ALWAYS_EAGER = not async

    all_buckets = []
    if kwargs.get('source'):
        source_buckets = util.parse_urls_into_groups(kwargs['source'])
        all_buckets.append(source_buckets)
    else:
        for source in registry.keys():
            source_buckets = util.parse_urls_into_groups(source)
            all_buckets.append(source_buckets)

    with open('all_sources.json', 'w') as outfile:
        json.dump(all_buckets, outfile)

    # for source_dict in all_buckets:
    #     for group in source_dict['uris']:
    #         process_uris_at_one_base_uri.delay(group['individual_uris'], async, kwargs=kwargs)


@task_autoretry(default_retry_delay=settings.CELERY_RETRY_DELAY, max_retries=0)
@events.logged(events.PROCESSSING_URIS, 'uri_processing')
def process_uris_at_one_base_uri(uri_list, async=False, **kwargs):
    settings.CELERY_ALWAYS_EAGER = not async

    for uri in uri_list:
        process_one_uri.delay(uri, kwargs=kwargs)


@task_autoretry(default_retry_delay=settings.CELERY_RETRY_DELAY, max_retries=0, rate_limit='5/s')
@events.logged(events.PROCESSSING_URIS, 'uri_processing')
def process_one_uri(uri, **kwargs):
    processing.process_uris(
        source=uri['source'],
        docID=uri['docID'],
        uri=uri['uri'],
        uritype=uri['uritype'],
        kwargs=kwargs
    )


@app.task
def migrate(migration, sources=tuple(), async=False, dry=True, group_size=1000, **kwargs):
    from scrapi.migrations import documents

    docs = documents(*sources)
    if async:
        segment = list(islice(docs, group_size))
        while segment:
            migration.s(segment, sources=sources, dry=dry, **kwargs).apply_async()
            segment = list(islice(docs, group_size))
    else:
        for doc in docs:
            migration((doc,), sources=sources, dry=dry, **kwargs)

    if dry:
        logger.info('Dry run complete')

    logger.info('Documents processed for migration {}'.format(str(migration)))


@app.task
def migrate_to_source_partition(dry=True, async=False):
    from scrapi import migrations
    count = 0
    for doc in migrations.documents_old():
        count += 1
        if async:
            migrations.document_v2_migration.s(doc, dry=dry).apply_async()
        else:
            migrations.document_v2_migration(doc, dry=dry)
    if dry:
        logger.info('Dry run complete')
    logger.info('{} documents processed for migration {}'.format(count, str(migrations.document_v2_migration)))
