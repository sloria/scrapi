import vcr
import datetime
from lxml import etree

import mock

from django import forms
from django.utils import timezone
from django.test import TestCase, RequestFactory, Client

from api.provider_registration import views
from api.provider_registration import utils
from api.provider_registration import validators
from api.provider_registration.models import RegistrationInfo
from api.provider_registration.forms import InitialProviderForm, OAIProviderForm, ContactInfoForm


class RegistrationMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = RegistrationInfo(registration_date=time)
        self.assertEqual(future_question.was_registered_recently(), False)

    def test_unicode_name(self):
        time = timezone.now() + datetime.timedelta(days=30)
        registraion = RegistrationInfo(
            provider_long_name='SquaredCircle Digest',
            registration_date=time
        )
        self.assertEqual(unicode(registraion), 'SquaredCircle Digest')


class RegistrationFormTests(TestCase):

    @vcr.use_cassette('tests/vcr/oai_response.yaml')
    def test_valid_oai_data(self):
        form = InitialProviderForm({
            'provider_long_name': 'Booyaka Booyaka',
            'reg_id': 1,
            'base_url': 'http://repository.stcloudstate.edu/do/oai/',
            'description': 'A description',
            'oai_provider': True
        })
        self.assertTrue(form.is_valid())

    @vcr.use_cassette('tests/vcr/other_response.yaml')
    def test_valid_other_data(self):
        form = InitialProviderForm({
            'provider_long_name': 'Devon - Get the Tables',
            'base_url': 'http://wwe.com',
            'description': 'A description',
            'reg_id': 1,
            'oai_provider': False
        })
        self.assertTrue(form.is_valid())

    def test_misformed_url(self):
        form = InitialProviderForm({
            'contact_name': 'BubbaRay Dudley',
            'contact_email': 'BullyRay@dudleyboyz.net',
            'provider_long_name': 'Devon - Get the Tables',
            'base_url': 'DEVONGETTHETABLLESSSSSS',
            'description': 'A description',
            'oai_provider': False
        })
        self.assertFalse(form.is_valid())

    def test_formed_not_valid(self):
        form = InitialProviderForm({
            'contact_name': 'BubbaRay Dudley',
            'contact_email': 'BullyRay@dudleyboyz.net',
            'provider_long_name': 'Devon - Get the Tables',
            'base_url': 'http://notreallyaurul.nope',
            'description': 'A description',
            'oai_provider': False
        })
        self.assertFalse(form.is_valid())

    @vcr.use_cassette('tests/vcr/oai_response.yaml')
    def test_missing_contact_name(self):
        form = InitialProviderForm({
            'contact_name': '',
            'contact_email': 'BullyRay@dudleyboyz.net',
            'provider_long_name': 'Devon - Get the Tables',
            'base_url': 'http://repository.stcloudstate.edu/do/oai/',
            'description': 'A description',
            'oai_provider': True
        })
        self.assertFalse(form.is_valid())

    @vcr.use_cassette('tests/vcr/oai_response.yaml')
    def test_missing_contact_email(self):
        form = InitialProviderForm({
            'contact_name': 'Spike Dudley',
            'contact_email': '',
            'provider_long_name': 'Devon - Get the Tables',
            'base_url': 'http://repository.stcloudstate.edu/do/oai/',
            'description': 'A description',
            'oai_provider': True
        })
        self.assertFalse(form.is_valid())

    @vcr.use_cassette('tests/vcr/oai_response.yaml')
    def test_malformed_contact_email(self):
        form = InitialProviderForm({
            'contact_name': 'Spike Dudley',
            'contact_email': 'email',
            'provider_long_name': 'Devon - Get the Tables',
            'base_url': 'http://repository.stcloudstate.edu/do/oai/',
            'description': 'A description',
            'oai_provider': True
        })
        self.assertFalse(form.is_valid())

    @vcr.use_cassette('tests/vcr/oai_response.yaml')
    def test_missing_provider_name(self):
        form = InitialProviderForm({
            'contact_name': 'Spike Dudley',
            'contact_email': 'email@email.com',
            'provider_long_name': '',
            'base_url': 'http://repository.stcloudstate.edu/do/oai/',
            'description': 'A description',
            'oai_provider': True
        })
        self.assertFalse(form.is_valid())

    def test_contact_info_valid(self):
        form = ContactInfoForm({
            'contact_email': 'email@email.com',
            'contact_name': 'A REAL NAME'
        })
        self.assertTrue(form.is_valid())


class TestOAIProviderForm(TestCase):

    @vcr.use_cassette('tests/vcr/oai_response.yaml')
    def test_valid_oai_data(self):
        approved_set_set = [('totally', 'approved')]
        form = OAIProviderForm({
            'provider_long_name': 'SuperCena',
            'base_url': 'http://repository.stcloudstate.edu/do/oai/',
            'property_list': "some, properties",
            'approved_sets': ["totally"],
            'reg_id': 1
        }, choices=approved_set_set)
        self.assertTrue(form.is_valid())


class ViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        # self.tree = ElementTree()

    def test_get_index(self):
        request = self.factory.get('/')
        view = views.index(request)
        self.assertEqual(view.status_code, 200)

    def test_get_provider_detail(self):
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://repository.stcloudstate.edu/do/oai/',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()

        response = self.client.get('provider_registration/provider_detail/Stardust Weekly/')
        self.assertEqual(response.status_code, 404)  # TODO - this is broken

    def test_get_contact_info(self):
        request = self.factory.get('provider_registration/contact_information/')
        view_processing = views.get_contact_info(request)
        self.assertEqual(view_processing.status_code, 200)

    def test_post_incorrect_contact_info(self):
        request = self.factory.post('provider_registration/contact_information/')
        view_processing = views.get_contact_info(request)
        root = etree.fromstring(view_processing.content)
        form_element = root.xpath('//form')[0]
        error = form_element.getchildren()[0]
        self.assertEqual(error.text, 'Please correct the errors below.')

    def test_post_contact_info(self):
        info = {'contact_name': 'Fabulous Moolah', 'contact_email': 'moolah@moolah.com'}
        request = self.factory.post('provider_registration/contact_information/', info)
        view_processing = views.get_contact_info(request)
        root = etree.fromstring(view_processing.content)
        form_element = root.xpath('//form')[0]
        new_form_title = form_element.getchildren()[0].text
        self.assertEqual(new_form_title, 'Metadata Sharing')

    def test_post_some_incorrect_contact_info(self):
        info = {'contact_name': '', 'contact_email': 'moolah@moolah.com'}
        request = self.factory.post('provider_registration/contact_information/', info)
        view_processing = views.get_contact_info(request)
        root = etree.fromstring(view_processing.content)
        form_element = root.xpath('//form')[0]
        error = form_element.getchildren()[0]
        self.assertEqual(error.text, 'Please correct the error below.')

    def test_save_metadata_render_provider(self):
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://repository.stcloudstate.edu/do/oai/',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        meta_form = {
            'meta_tos': True,
            'meta_rights': False,
            'meta_privacy': False,
            'meta_sharing': True,
            'meta_license_cc0': False,
            'reg_id': RegistrationInfo.objects.last().pk
        }
        request = self.factory.post('provider_registration/provider_information/', meta_form)
        response = views.save_metadata_render_provider(request)
        root = etree.fromstring(response.content)
        form_element = root.xpath('//form')
        new_form_title = form_element[0].getchildren()[0].text
        self.assertEqual(new_form_title, 'Basic Provider Information')

    @mock.patch('api.provider_registration.utils.get_oai_properties')
    @vcr.use_cassette('tests/vcr/oai_response_datequery1.yaml')
    def test_render_oai_provider_form(self, mock_properties):
        mock_properties.return_value = {'properties': 'shtuff', 'sets': [('star', 'dust')]}
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://repository.stcloudstate.edu/do/oai/',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        request = self.factory.post('provider_registration/register/')
        name = "Some Name"
        base_url = 'http://repository.stcloudstate.edu/do/oai/'
        reg_id = RegistrationInfo.objects.last().pk
        api_docs = ''
        rate_limit = ''
        description = 'A thing again!'
        response = views.render_oai_provider_form(request, name, base_url, reg_id, api_docs, rate_limit, description)
        root = etree.fromstring(response.content)
        form_element = root.xpath('//form')[0]
        title = form_element.getchildren()[0]
        self.assertEqual(title.text, 'Provider Information')

    @vcr.use_cassette('tests/vcr/invalid_xml_oai_dataquery3.yaml')
    def test_render_oai_provider_form_invaid_xml(self):
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://wwe.com',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        request = self.factory.post('registration/register/')
        name = "Some Name"
        base_url = 'http://wwe.com'
        reg_id = RegistrationInfo.objects.last().pk
        api_docs = ''
        rate_limit = ''
        description = 'A thing again!'
        response = views.render_oai_provider_form(request, name, base_url, reg_id, api_docs, rate_limit, description)
        root = etree.fromstring(response.content)
        form_element = root.xpath('//form')[0]
        title = form_element.getchildren()[0]
        self.assertEqual(title.text, 'Simple Provider Information')

    @mock.patch('api.provider_registration.utils.get_session_item')
    @vcr.use_cassette('tests/vcr/invalid_xml_oai_redirect.yaml')
    def test_render_simple_oai_form(self, mocked_id):
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://wwe.com',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        mocked_id.return_value = RegistrationInfo.objects.last().pk
        request = self.factory.post('provider_registration/register/')
        response = views.redirect_to_simple_oai(request)
        self.assertEqual(response.status_code, 200)

        root = etree.fromstring(response.content)
        form_element = root.xpath('//form')[0]
        title = form_element.getchildren()[0]
        self.assertEqual(title.text, 'Simple Provider Information')

    def test_registration_complete(self):
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://wwe.com',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        request = self.factory.get('/')
        provider_long_name = 'The COSMIC KEEEEEY'
        base_url = 'http://wwe.com'
        rate_limit = ''
        api_docs = ''
        description = 'A thing!'
        new_registration = RegistrationInfo.objects.last()
        reg_id = new_registration.pk
        success = views.save_other_provider(request, provider_long_name, base_url, reg_id, api_docs, rate_limit, description)
        self.assertTrue(success)
        self.assertFalse(new_registration.registration_complete)


class ViewMethodTests(TestCase):

    @mock.patch('api.provider_registration.utils.get_oai_properties')
    @vcr.use_cassette('tests/vcr/oai_response_datequery2.yaml')
    def test_valid_oai_url(self, mock_properties):
        RegistrationInfo(
            provider_long_name='The Old Stardust Weekly',
            base_url='http://aurl.com',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        mock_properties.return_value = {'properties': 'shtuff', 'sets': [('star', 'dust')]}
        provider_long_name = 'New Stardust Weekly'
        base_url = 'http://repository.stcloudstate.edu/do/oai/'
        reg_id = RegistrationInfo.objects.last().pk
        api_docs = ''
        rate_limit = ''
        description = 'COSMC EKEEEEEEYYYYy'
        success = views.save_oai_info(provider_long_name, base_url, reg_id, api_docs, rate_limit, description)
        self.assertTrue(success['value'])
        self.assertEqual(success['reason'], 'New Stardust Weekly registered and saved successfully')

    @vcr.use_cassette('tests/vcr/other_response_oai.yaml')
    def test_invalid_oai_url(self):
        RegistrationInfo(
            provider_long_name='Golddust Monthly',
            base_url='http://aurl.com',
            property_list=['some', 'properties'],
            approved_sets=['some', 'sets'],
            registration_date=timezone.now()
        ).save()
        reg_id = RegistrationInfo.objects.last().pk
        base_url = 'http://aurl.com'
        api_docs = ''
        rate_limit = ''
        provider_long_name = 'Golddust Monthly'
        description = 'SHAAAwwwwww'
        success = views.save_oai_info(provider_long_name, base_url, reg_id, api_docs, rate_limit, description)
        self.assertFalse(success['value'])
        self.assertEqual(success['reason'], 'OAI Information could not be automatically processed.')

    @vcr.use_cassette('tests/vcr/other_response_oai.yaml')
    def test_save_other_provider(self):
        RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://repository.stcloudstate.edu/do/oai/',
            property_list=['some', 'properties'],
            approved_sets="[('publication:some', 'sets')]",
            registration_date=timezone.now()
        ).save()
        provider_long_name = 'The COSMIC KEEEEEY'
        base_url = 'http://wwe.com'
        rate_limit = ''
        api_docs = ''
        description = 'A thing!'
        new_registration = RegistrationInfo.objects.last()
        reg_id = new_registration.pk
        success = views.save_other_info(provider_long_name, base_url, reg_id, api_docs, rate_limit, description)
        self.assertTrue(success)


class TestUtils(TestCase):

    def test_format_set_choices(self):
        test_data = RegistrationInfo(
            provider_long_name='Stardust Weekly',
            base_url='http://repository.stcloudstate.edu/do/oai/',
            property_list=['some', 'properties'],
            approved_sets="[('publication:some', 'sets')]",
            registration_date=timezone.now()
        )

        formatted_sets = utils.format_set_choices(test_data)
        self.assertEqual(formatted_sets, set([('some', 'sets')]))


class TestValidators(TestCase):

    @vcr.use_cassette('tests/vcr/oai_response_identify.yaml')
    def test_valid_oai_url(self):
        url = 'http://repository.stcloudstate.edu/do/oai/'
        oai_validator = validators.ValidOAIURL()
        call = oai_validator(url)
        self.assertTrue(call)

    @vcr.use_cassette('tests/vcr/other_response_identify.yaml')
    def test_invalid_oai_url(self):
        url = 'http://wwe.com'
        oai_validator = validators.ValidOAIURL()

        with self.assertRaises(forms.ValidationError):
            oai_validator(url)

    @vcr.use_cassette('tests/vcr/oai_response_invalid_identify.yaml')
    def test_invalid_oai_url_with_xml(self):
        url = 'http://www.osti.gov/scitech/scitechxml?EntryDateFrom=02%2F02%2F2015&page=0'
        oai_validator = validators.ValidOAIURL()

        with self.assertRaises(forms.ValidationError):
            oai_validator(url)

    @vcr.use_cassette('tests/vcr/other_response_404.yaml')
    def test_url_returns_404(self):
        url = 'https://github.com/erinspace/thisisnotreal'
        url_validator = validators.URLResolves()

        with self.assertRaises(forms.ValidationError):
            url_validator(url)

    @vcr.use_cassette('tests/vcr/other_response_404_oai.yaml')
    def test_oai_url_returns_404(self):
        url = 'https://github.com/erinspace/thisisnotreal'
        url_validator = validators.ValidOAIURL()

        with self.assertRaises(forms.ValidationError):
            url_validator(url)
