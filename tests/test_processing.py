import mock
import pytest

from scrapi import settings

settings.DEBUG = False

from scrapi import processing

BLACKHOLE = lambda *_, **__: None


@pytest.fixture
def get_processor(monkeypatch):
    mock_get_proc = mock.MagicMock()
    monkeypatch.setattr('scrapi.processing.get_processor', mock_get_proc)
    return mock_get_proc


def raise_exception(x):
    if x == 'storage':
        raise Exception('Reasons')
    return mock.Mock()


def test_normalized_calls_all(get_processor):
    stored_methods = []
    for processor in processing.normalized_processors:
        stored_methods.append(processor.process_normalized)
        processor.process_normalized = mock.Mock()

    processing.process_normalized(mock.MagicMock(), mock.MagicMock(), {})

    for fn, processor in zip(stored_methods, processing.normalized_processors):
        processor.process_normalized.assert_called
        processor.process_normalized = fn



def test_raw_calls_all(get_processor):
    stored_methods = []
    for processor in processing.raw_processors:
        stored_methods.append(processor.process_raw)
        processor.process_raw = mock.Mock()

    processing.process_raw(mock.MagicMock(), {})

    for fn, processor in zip(stored_methods, processing.raw_processors):
        processor.process_raw.assert_called
        processor.process_raw = fn


def test_normalized_calls_all_throwing(get_processor):
    get_processor.side_effect = raise_exception

    with pytest.raises(Exception):
        processing.process_normalized(mock.MagicMock(), mock.MagicMock(), {})


def test_raw_calls_all_throwing(get_processor):
    get_processor.side_effect = raise_exception

    with pytest.raises(Exception):
        processing.process_raw(mock.MagicMock(), {})


def test_raises_on_bad_processor():
    with pytest.raises(NotImplementedError):
        processing.get_processor("Baby, You're never there.")
