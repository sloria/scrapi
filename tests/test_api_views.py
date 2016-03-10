import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")

import django
from django.test import TestCase 
from rest_framework.test import APIRequestFactory, APITestCase, APIClient, force_authenticate
from dateutil.parser import parse
from api.webview.views import DocumentList, status, institutions, DocumentsByProviderUpdatedDateTime
from api.webview.models import Document

django.setup()


class APIViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_document_view(self):
        view = DocumentList.as_view()
        request = self.factory.get(
            '/documents/'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_source_view(self):
        view = DocumentList.as_view()
        request = self.factory.get(
            '/documents/dudley_weekly/'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_individual_view(self):
        view = DocumentList.as_view()
        request = self.factory.get(
            '/documents/dudley_weekly/dudley1'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_status(self):
        view = status
        request = self.factory.get(
            '/status'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_institutions(self):
        view = institutions
        request = self.factory.post(
            '/institutions/',
            {'query': {"query": {"match": {"name": {"query": "University"}}}, "from": 0, "size": 10}},
            format='json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 200)
    def test_exclude_non_normalized_documents(self):
        view = DocumentList.as_view()
        create_document(source="bad",normalized=None)
        create_document(source="good",normalized="This is Normalized")
        request = self.factory.get(
            '/documents/'
        )
        response = view(request)        
        self.assertNotContains(response, "bad",
                            status_code=200)
        self.assertContains(response, "good", status_code=200)
        print(response)


class APIViewTests2(APITestCase):

    def test_query_search_by_providerupdatedtime(self):
        view = DocumentsByProviderUpdatedDateTime.as_view()
        create_new_document(source = "tooearly",providerUpdatedDateTime= parse("2012-01-01"))
        create_new_document(source = "rightontime", providerUpdatedDateTime= parse("2013-01-05"))
        create_new_document(source= "toolate", providerUpdatedDateTime = parse("2015-01-01"))
        response = self.client.get('/documents/from=2013-01-01&until=2014-12-30/', kwargs= {'from':"2013-01-01",'until':'2014-12-30'})
        force_authenticate(response)
        self.assertNotContains(response, "tooearly", status_code=200)
        self.assertContains(response, "rightontime", status_code=200)
        self.assertNotContains(response, "toolate", status_code =200)


def create_new_document(source,providerUpdatedDateTime):
        return Document.objects.create(source = source, providerUpdatedDateTime = providerUpdatedDateTime)
def create_document(source,normalized):
        return Document.objects.create(source= source,normalized= normalized)







