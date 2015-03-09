import mock
import json
import pytest

from scrapi import requests


@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    mock_req = mock.Mock()
    monkeypatch.setattr(requests, 'requests', mock_req)
    return mock_req


@pytest.fixture(autouse=True)
def mock_record_transactions(monkeypatch):
    monkeypatch.setattr(requests.settings, 'RECORD_HTTP_TRANSACTIONS', True)


class TestSettings(object):
    def test_record_or_load_response_respects_record_false(self, mock_requests, monkeypatch):
        mock_rec_or_load = mock.Mock()
        monkeypatch.setattr(requests.settings, 'RECORD_HTTP_TRANSACTIONS', False)
        monkeypatch.setattr(requests, 'record_or_load_response', mock_rec_or_load)

        requests.get('foo')

        assert not mock_rec_or_load.called
        assert mock_requests.request.called_once_with('get', 'foo')

    def test_record_or_load_response_respects_record_true(self, mock_requests, monkeypatch):
        mock_rec_or_load = mock.Mock()
        monkeypatch.setattr(requests, 'record_or_load_response', mock_rec_or_load)

        requests.get('foo')

        assert mock_rec_or_load.called_once_with('get', 'foo')
        assert mock_requests.request.called_once_with('get', 'foo')


@pytest.mark.cassandra
class TestModel(object):
    def test_json_works(self):
        data = {'totally': 'dyle'}

        resp = requests.HarvesterResponse(content=json.dumps(data))

        assert resp.json == data
        assert resp.content == json.dumps(data)


@pytest.mark.cassandra
class TestCassandraIntegration(object):
    def test_record_or_load_loads(self, mock_requests, monkeypatch):
        requests.HarvesterResponse(ok=True, method='get', url='dinosaurs.sexy', content='rawr', headers_str="{}").save()

        resp = requests.get('dinosaurs.sexy')

        assert resp.headers == {}
        assert resp.content == 'rawr'
        assert not mock_requests.request.called
        assert isinstance(resp, requests.HarvesterResponse)

    def test_record_or_load_remakes(self, mock_requests, monkeypatch):
        mock_requests.request.return_value = mock.Mock(encoding='utf-8', content='rawr', status_code=200, headers={'tota': 'dyle'})
        requests.HarvesterResponse(ok=False, method='get', url='dinosaurs.sexy').save()

        model = requests.HarvesterResponse.get(method='get', url='dinosaurs.sexy')

        assert not model.ok
        assert model.method == 'get'
        assert model.url == 'dinosaurs.sexy'

        resp = requests.get('dinosaurs.sexy')

        model = requests.HarvesterResponse.get(method='get', url='dinosaurs.sexy')

        assert model.method == 'get'
        assert model.content == 'rawr'
        assert model.encoding == 'utf-8'
        assert model.status_code == 200
        assert model.url == 'dinosaurs.sexy'
        assert model.headers == {'tota': 'dyle'}
        assert model.headers_str == '{"tota": "dyle"}'
        assert isinstance(resp, requests.HarvesterResponse)

    def test_record_or_load_records(self, mock_requests, monkeypatch):
        mock_requests.request.return_value = mock.Mock(encoding='utf-8', content='rawr', status_code=200, headers={'tota': 'dyle'})

        resp = requests.get('dinosaurs.sexy')

        model = requests.HarvesterResponse.get(method='get', url='dinosaurs.sexy')

        assert model.method == 'get'
        assert model.content == 'rawr'
        assert model.encoding == 'utf-8'
        assert model.status_code == 200
        assert model.url == 'dinosaurs.sexy'
        assert model.headers == {'tota': 'dyle'}
        assert model.headers_str == '{"tota": "dyle"}'
        assert isinstance(resp, requests.HarvesterResponse)

    def test_record_or_load_logs_not_ok(self, mock_requests, monkeypatch):
        mock_log = mock.Mock()
        monkeypatch.setattr(requests.events, 'log_to_sentry', mock_log)
        mock_requests.request.return_value = mock.Mock(ok=False, encoding='utf-8', content='rawr', status_code=200, headers={'tota': 'dyle'})

        requests.get('dinosaurs.sexy')

        mock_log.assert_called_once_with('Got non-okay response code.', url='dinosaurs.sexy', method='get')


class TestRequestsApi(object):
    def test_get_calls_get(self, monkeypatch):
        mock_request = mock.Mock()
        monkeypatch.setattr(requests, 'record_or_load_response', mock_request)

        requests.get('test', tota='dyle')

        mock_request.assert_called_once_with('get', 'test', tota='dyle')

    def test_put_calls_put(self, monkeypatch):
        mock_request = mock.Mock()
        monkeypatch.setattr(requests, 'record_or_load_response', mock_request)

        requests.put('test', tota='dyle')

        mock_request.assert_called_once_with('put', 'test', tota='dyle')

    def test_post_calls_post(self, monkeypatch):
        mock_request = mock.Mock()
        monkeypatch.setattr(requests, 'record_or_load_response', mock_request)

        requests.post('test', tota='dyle')

        mock_request.assert_called_once_with('post', 'test', tota='dyle')

    def test_delete_calls_delete(self, monkeypatch):
        mock_request = mock.Mock()
        monkeypatch.setattr(requests, 'record_or_load_response', mock_request)

        requests.delete('test', tota='dyle')

        mock_request.assert_called_once_with('delete', 'test', tota='dyle')
