from django import forms
from api.provider_registration.validators import URLResolves


from api.provider_registration.models import RegistrationInfo


class ContactInfoForm(forms.ModelForm):
    contact_name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    contact_email = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    class Meta:
        model = RegistrationInfo
        fields = ['contact_name', 'contact_email']


class MetadataQuestionsForm(forms.ModelForm):
    reg_id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = RegistrationInfo
        fields = ['meta_tos', 'meta_rights', 'meta_privacy', 'meta_sharing',
                  'meta_license_cc0', 'reg_id']


class InitialProviderForm(forms.ModelForm):
    reg_id = forms.CharField(widget=forms.HiddenInput())
    provider_long_name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    api_docs = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}), required=False)
    rate_limit = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}), required=False)
    base_url = forms.URLField(validators=[URLResolves()], widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    class Meta:
        model = RegistrationInfo
        fields = ['provider_long_name', 'base_url', 'description', 'oai_provider',
                  'reg_id', 'rate_limit', 'api_docs']


class OAIProviderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        super(OAIProviderForm, self).__init__(*args, **kwargs)
        self.fields['approved_sets'].choices = self.choices

    reg_id = forms.CharField(widget=forms.HiddenInput())
    property_list = forms.CharField(widget=forms.HiddenInput)
    provider_long_name = forms.CharField(widget=forms.HiddenInput())
    base_url = forms.URLField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    approved_sets = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = RegistrationInfo
        fields = ['provider_long_name', 'base_url',
                  'property_list', 'approved_sets', 'reg_id']


class SimpleOAIProviderForm(forms.ModelForm):
    reg_id = forms.CharField(widget=forms.HiddenInput())
    property_list = forms.CharField(widget=forms.HiddenInput)
    provider_long_name = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = RegistrationInfo
        fields = ['provider_long_name', 'base_url', 'reg_id', 'approved_sets', 'property_list']


class OtherProviderForm(forms.ModelForm):
    reg_id = forms.CharField(widget=forms.HiddenInput())
    property_list = forms.CharField(widget=forms.HiddenInput)
    provider_long_name = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = RegistrationInfo
        fields = ['provider_long_name', 'base_url', 'reg_id', 'property_list']
