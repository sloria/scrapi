import pytest

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")

import django
django.setup()

from api.webview.models import Document

from django.test import TestCase
from scrapi.processing.postgres import PostgresProcessor
from . import utils
from scrapi.linter.document import RawDocument


test_db = PostgresProcessor()

# NORMALIZED = NormalizedDocument(utils.RECORD)
RAW = RawDocument(utils.RAW_DOC)


class DocumentTestCase(TestCase):

    @pytest.mark.django_db
    def test_raw_processing(self):
        test_db.process_raw(RAW)
        queryset = Document(docID='someID', source=RAW['source'])
        assert queryset.docID == RAW.attributes['docID']
