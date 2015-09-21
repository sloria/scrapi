from __future__ import unicode_literals

import mock
import pytest
from datetime import date

from scrapi import requests
from scrapi.base import OAIHarvester
from scrapi.linter import RawDocument

from .utils import TEST_OAI_DOC


request_url = 'http://validOAI.edu/?sonofaplumber'


@pytest.fixture(autouse=True)
def mock_maybe_load_response(monkeypatch):
    mock_mlr = mock.Mock()
    mock_mlr.return_value = requests.HarvesterResponse(
        ok=True,
        method='get',
        url=request_url.lower(),
        content=TEST_OAI_DOC,
    )
    mock_save = lambda x: x

    monkeypatch.setattr(requests, '_maybe_load_response', mock_mlr)
    monkeypatch.setattr(requests.HarvesterResponse, 'save', mock_save)


@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    mock_req = mock.Mock()
    monkeypatch.setattr(requests, 'requests', mock_req)
    return mock_req


@pytest.fixture(autouse=True)
def mock_record_transactions(monkeypatch):
    monkeypatch.setattr(requests.settings, 'RECORD_HTTP_TRANSACTIONS', True)


class TestHarvester(OAIHarvester):
    base_url = ''
    long_name = 'Test'
    short_name = 'test'
    url = 'test'
    property_list = ['type', 'source', 'publisher', 'format', 'date']
    verify = True

    def harvest(self, start_date=None, end_date=None, resume=True):
        start_date = date(2015, 3, 14)
        end_date = date(2015, 3, 16)

        records = self.get_records(request_url, start_date, end_date, resume)

        return [RawDocument({
            'doc': TEST_OAI_DOC,
            'source': 'test',
            'filetype': 'XML',
            'docID': "1"
        }) for record in records]


class TestOAIHarvester(object):

    def setup_method(self, method):
        self.harvester = TestHarvester()

    def test_normalize(self):
        results = [
            self.harvester.normalize(record) for record in self.harvester.harvest()
        ]

        for res in results:
            assert res['title'] == 'Test'
