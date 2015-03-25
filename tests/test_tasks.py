import mock
import pytest

from scrapi import tasks
from scrapi import settings
from scrapi.linter import RawDocument


settings.USE_FLUENT = False
BLACKHOLE = lambda *_, **__: None


@pytest.fixture
def raw_doc():
    return RawDocument({
        'doc': 'bar',
        'docID': u'foo',
        'source': u'test',
        'filetype': u'xml',
    })


@pytest.fixture
def raw_docs():
    return [
        RawDocument({
            'doc': str(x),
            'docID': unicode(x),
            'source': u'test',
            'filetype': u'xml',
        })
        for x in xrange(11)
    ]


def test_run_harvester_calls(monkeypatch):
    mock_harvest = mock.MagicMock()
    mock_begin_norm = mock.MagicMock()

    monkeypatch.setattr('scrapi.tasks.harvest', mock_harvest)
    monkeypatch.setattr('scrapi.tasks.begin_normalization', mock_begin_norm)

    tasks.run_harvester('test')

    assert mock_harvest.si.called
    assert mock_begin_norm.s.called

    mock_begin_norm.s.assert_called_once_with('test')
    mock_harvest.si.assert_called_once_with('test', 'TIME', days_back=1)


def test_run_harvester_daysback(monkeypatch):
    mock_harvest = mock.MagicMock()
    mock_begin_norm = mock.MagicMock()

    monkeypatch.setattr('scrapi.tasks.harvest', mock_harvest)
    monkeypatch.setattr('scrapi.tasks.begin_normalization', mock_begin_norm)

    tasks.run_harvester('test', days_back=10)

    assert mock_harvest.si.called
    assert mock_begin_norm.s.called

    mock_begin_norm.s.assert_called_once_with('test')
    mock_harvest.si.assert_called_once_with('test', 'TIME', days_back=10)


@pytest.mark.usefixtures('harvester')
def test_harvest_runs_harvest(harvester):
    tasks.harvest('test', 'TIME')

    assert harvester.harvest.called


@pytest.mark.usefixtures('harvester')
def test_harvest_days_back(harvester):
    _, timestamps = tasks.harvest('test', 'TIME', days_back=10)

    keys = ['harvestFinished', 'harvestTaskCreated', 'harvestStarted']

    for key in keys:
        assert key in timestamps.keys()

    assert harvester.harvest.called
    harvester.harvest.assert_called_once_with(days_back=10)


@pytest.mark.usefixtures('harvester')
def test_harvest_raises(harvester):
    harvester.harvest.side_effect = KeyError('testing')

    with pytest.raises(KeyError) as e:
        tasks.harvest('test', 'TIME')

    assert e.value.message == 'testing'


def test_begin_normalize_starts(raw_docs, monkeypatch):
    mock_norm = mock.MagicMock()
    mock_praw = mock.MagicMock()
    mock_pnorm = mock.MagicMock()

    monkeypatch.setattr('scrapi.tasks.normalize', mock_norm)
    monkeypatch.setattr('scrapi.tasks.process_raw', mock_praw)
    monkeypatch.setattr('scrapi.tasks.process_normalized', mock_pnorm)

    timestamps = {}
    tasks.begin_normalization((raw_docs, timestamps), 'test')

    assert mock_norm.si.call_count == 11
    assert mock_pnorm.s.call_count == 11
    assert mock_praw.delay.call_count == 11

    for x in raw_docs:
        mock_pnorm.s.assert_any_call(x)
        mock_praw.delay.assert_any_call(x)
        mock_norm.si.assert_any_call(x, 'test')


def test_process_raw_calls(raw_doc, monkeypatch):
    pmock = mock.Mock()

    monkeypatch.setattr('scrapi.tasks.storage.process_raw', pmock)

    tasks.process_raw(raw_doc)

    pmock.assert_called_once_with(raw_doc, {})


def test_process_norm_calls(raw_doc, monkeypatch):
    pmock = mock.Mock()

    monkeypatch.setattr('scrapi.tasks.storage.process_normalized', pmock)

    tasks.process_normalized(raw_doc, raw_doc)

    pmock.assert_called_once_with(raw_doc, raw_doc, {})
