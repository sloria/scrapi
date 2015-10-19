import logging

import requests
import collections
from lxml.etree import XMLSyntaxError

from django.utils import timezone
from django.shortcuts import render
from django.forms.util import ErrorList
from django.views.decorators.clickjacking import xframe_options_exempt

from api.provider_registration import utils

from api.provider_registration.models import RegistrationInfo
from api.provider_registration.forms import OAIProviderForm, OtherProviderForm, InitialProviderForm, ContactInfoForm, MetadataQuestionsForm, SimpleOAIProviderForm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLACEHOLDER = 'temp_value'


@xframe_options_exempt
def index(request):
    providers_orig = requests.get('https://osf.io/api/v1/share/providers/').json()['providerMap']
    doc_count = requests.get('https://osf.io/api/v1/share/search/?v=1').json()['count']
    doc_count = format(doc_count, ",d")

    providers = collections.OrderedDict(sorted(providers_orig.items()))

    number_of_providers = len(providers.keys())
    context = {'providers': providers, 'number_of_providers': number_of_providers, 'doc_count': doc_count}

    return render(request, 'provider_registration/index.html', context)


@xframe_options_exempt
def get_contact_info(request):
    """ Shows initial provider form
    """
    if request.method == 'GET':
        form = ContactInfoForm()
        return render(
            request,
            'provider_registration/contact_information.html',
            {'form': form}
        )
    else:
        form = ContactInfoForm(request.POST)
        if form.is_valid():
            contact_name = request.POST.get('contact_name')
            contact_email = request.POST.get('contact_email')
            reg_id = save_contact_info(contact_name, contact_email)
            form = MetadataQuestionsForm({'reg_id': reg_id, 'meta_license': ' '})
            return render(
                request,
                'provider_registration/metadata_questions.html',
                {'form': form}
            )
        else:
            return render(
                request,
                'provider_registration/contact_information.html',
                {'form': form}
            )


def save_contact_info(contact_name, contact_email):
    logger.info('Saving provider with contact name {} and email {}'.format(contact_name, contact_email))
    RegistrationInfo(
        base_url=PLACEHOLDER,
        contact_name=contact_name,
        contact_email=contact_email,
        provider_long_name=PLACEHOLDER,
        registration_date=timezone.now()
    ).save()
    new_registration = RegistrationInfo.objects.last()
    return new_registration.id


@xframe_options_exempt
def save_metadata_render_provider(request):
    """
    Saves metadata info
    Shows basic provider questions form
    """
    form = MetadataQuestionsForm(request.POST)
    if form.is_valid():
        reg_id = request.POST.get('reg_id')
        current_registration = RegistrationInfo.objects.get(id=reg_id)

        all_clear = []

        if request.POST.get('meta_tos'):
            current_registration.meta_tos = True
            all_clear.append('meta_tos')

        if request.POST.get('meta_rights'):
            current_registration.meta_rights = True
            all_clear.append('meta_rights')

        if request.POST.get('meta_privacy'):
            current_registration.meta_privacy = True
            all_clear.append('meta_privacy')

        if request.POST.get('meta_sharing'):
            current_registration.meta_sharing = True
            all_clear.append('meta_sharing')

        if request.POST.get('meta_license_cc0'):
            current_registration.meta_license_cc0 = True
            all_clear.append('meta_license_cc0')

        current_registration.save()

        if len(all_clear) < 5:
            utils.compose_desk_email(reg_type='incomplete')
            current_registration.registration_complete = True
            current_registration.save()
            return render(
                request,
                'provider_registration/registration_paused.html',
            )
        else:
            form = InitialProviderForm(initial={
                'reg_id': reg_id
            })
            return render(
                request,
                'provider_registration/provider_questions.html',
                {'form': form}
            )

    else:
        return render(
            request,
            'provider_registration/metadata_questions.html',
            {'form': form}
        )


def save_other_info(provider_long_name, base_url, reg_id, api_docs, rate_limit, description):
    object_to_update = RegistrationInfo.objects.get(id=reg_id)

    object_to_update.api_docs = api_docs
    object_to_update.base_url = base_url
    object_to_update.rate_limit = rate_limit
    object_to_update.description = description
    object_to_update.registration_date = timezone.now()
    object_to_update.provider_long_name = provider_long_name
    object_to_update.metadata_complete = True
    object_to_update.save()

    return True


def save_oai_info(provider_long_name, base_url, reg_id, api_docs, rate_limit, description):
    """ Gets and saves information about the OAI source
    """
    success = {'value': False, 'reason': 'XML Not Valid'}
    print('saving OAI info...')
    object_to_update = RegistrationInfo.objects.get(id=reg_id)
    object_to_update.api_docs = api_docs
    object_to_update.base_url = base_url
    object_to_update.description = description
    object_to_update.rate_limit = rate_limit
    object_to_update.registration_date = timezone.now()
    object_to_update.provider_long_name = provider_long_name
    object_to_update.metadata_complete = True
    object_to_update.oai_provider = True
    object_to_update.save()

    try:
        oai_properties = utils.get_oai_properties(base_url)

        object_to_update.approved_sets = oai_properties['sets']
        object_to_update.property_list = oai_properties['properties']
        object_to_update.save()

        success['value'] = True
        success['reason'] = '{} registered and saved successfully'.format(provider_long_name)

    except XMLSyntaxError:
        success['reason'] = 'XML Not Valid'

    except ValueError:
        success['reason'] = 'OAI Information could not be automatically processed.'

    logger.info(success['reason'])
    return success


@xframe_options_exempt
def render_oai_provider_form(request, name, base_url, reg_id, api_docs, rate_limit, description):
    saving_successful = save_oai_info(name, base_url, reg_id, api_docs, rate_limit, description)
    if saving_successful['value']:
        pre_saved_data = RegistrationInfo.objects.get(id=reg_id)

        approved_set_set = utils.format_set_choices(pre_saved_data)

        # render an OAI form with the request data filled in
        form = OAIProviderForm(
            {
                'reg_id': reg_id,
                'base_url': base_url,
                'provider_long_name': name,
                'property_list': pre_saved_data.property_list
            },
            choices=sorted(approved_set_set, key=lambda x: x[1])
        )
        return render(
            request,
            'provider_registration/oai_registration_form.html',
            {'form': form, 'name': name, 'base_url': base_url}
        )
    elif saving_successful['reason'] == 'XML Not Valid':
        form = InitialProviderForm(request.POST)
        form.is_valid()
        form._errors["base_url"] = ErrorList(["OAI-PMH XML not valid, please enter a valid OAI PMH url"])
        return render(
            request,
            'provider_registration/provider_questions.html',
            {'form': form}
        )
    elif saving_successful['reason'] == 'OAI Information could not be automatically processed.':
        form = SimpleOAIProviderForm(initial={
            'reg_id': reg_id,
            'base_url': base_url,
            'provider_long_name': name,
            'property_list': 'enter properties here'
        })
        return render(
            request,
            'provider_registration/simple_oai_registration_form.html',
            {'form': form, 'name': name, 'base_url': base_url.strip()}
        )


@xframe_options_exempt
def redirect_to_simple_oai(request):
    reg_id = utils.get_session_item(request, 'reg_id')
    new_registration = RegistrationInfo.objects.get(id=reg_id)

    name = new_registration.provider_long_name
    base_url = new_registration.base_url
    reg_id = new_registration.id

    form = SimpleOAIProviderForm(initial={
        'reg_id': reg_id,
        'base_url': base_url,
        'provider_long_name': name,
        'property_list': 'enter properties'
    })
    return render(
        request,
        'provider_registration/simple_oai_registration_form.html',
        {'form': form, 'name': name, 'base_url': base_url.strip()}
    )


@xframe_options_exempt
def save_other_provider(request, name, base_url, reg_id, api_docs, rate_limit, description):
    saving_successful = save_other_info(name, base_url, reg_id, api_docs, rate_limit, description)
    object_to_update = RegistrationInfo.objects.get(id=reg_id)
    if saving_successful:
        object_to_update.registration_complete = True
        object_to_update.save()
        return render(
            request,
            'provider_registration/confirmation.html',
            {'provider': name}
        )


def update_oai_entry(request):
    choices = {(item, item) for item in request.POST['approved_sets']}
    form_data = OAIProviderForm(request.POST, choices=choices)
    object_to_update = RegistrationInfo.objects.get(id=request.POST['reg_id'])

    object_to_update.property_list = form_data['property_list'].value()
    object_to_update.approved_sets = str(form_data['approved_sets'].value())
    object_to_update.registration_complete = True

    object_to_update.save()
    return form_data


def update_other_entry(request):
    form_data = OtherProviderForm(request.POST)
    object_to_update = RegistrationInfo.objects.get(id=request.POST['reg_id'])
    object_to_update.property_list = form_data['property_list'].value()
    object_to_update.registration_complete = True

    object_to_update.save()
    return form_data


@xframe_options_exempt
def register_provider(request):
    """ Function to register a provider. This does all the work for
    registration, calling out to other functions for processing
    """
    ## TODO - request.POST['property_list'] is '' here and so this needs to be fixed!!!
    if not request.POST.get('property_list'):
        request.session['reg_id'] = request.POST['reg_id']
        # this is the initial post, and needs to be checked
        form = InitialProviderForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                'provider_registration/provider_questions.html',
                {'form': form}
            )
        reg_id = request.POST['reg_id']
        api_docs = request.POST['api_docs']
        base_url = request.POST['base_url']
        rate_limit = request.POST['rate_limit']
        name = request.POST['provider_long_name']
        description = request.POST['description']
        # if it's a first request and not an oai request, render the other provider form
        if not request.POST.get('oai_provider'):
            form = save_other_provider(request, name, base_url, reg_id, api_docs, rate_limit, description)
            return form
        else:
            # If it's made it this far, request is an OAI provider
            form = render_oai_provider_form(request, name, base_url, reg_id, api_docs, rate_limit, description)
            return form
    else:
        # Update the requested entries
        if request.POST.get('approved_sets', False):
            form_data = update_oai_entry(request)
        else:
            form_data = update_other_entry(request)

        return render(
            request,
            'provider_registration/confirmation.html',
            {'provider': form_data['provider_long_name'].value()}
        )
