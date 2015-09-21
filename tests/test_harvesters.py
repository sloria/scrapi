import logging

import vcr
import pytest

from scrapi import base
from scrapi import registry, requests

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('harvester_name', filter(lambda x: x != 'test', sorted(map(str, registry.keys()))))
def test_harvester(monkeypatch, harvester_name, *args, **kwargs):
    monkeypatch.setattr(requests.time, 'sleep', lambda *_, **__: None)
    base.settings.RAISE_IN_TRANSFORMER = True

    harvester = registry[harvester_name]

    with vcr.use_cassette('tests/vcr/{}.yaml'.format(harvester_name), match_on=['host'], record_mode='none'):
        harvested = harvester.harvest(page_limit=1)
        assert len(harvested) > 0

    normalized = list(filter(lambda x: x is not None, map(harvester.normalize, harvested[:25])))
    assert len(normalized) > 0
