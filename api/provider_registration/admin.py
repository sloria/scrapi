from django.contrib import admin
from api.provider_registration.models import RegistrationInfo


class RegistrationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contact', {
            'fields': [
                'contact_name',
                'contact_email',
            ]
        }),
        ('Provider', {
            'fields': [
                'api_docs',
                'base_url',
                'description',
                'oai_provider',
                'provider_short_name',
                'provider_long_name',
                'rate_limit'
            ]
        }),
        ('Harvester', {
            'fields': [
                'base_url',
                'property_list',
                'approved_sets',
                'per_request_rate_limit',
                'active_provider'
            ]
        }),
        ('Metadata', {
            'fields': [
                'meta_tos',
                'meta_rights',
                'meta_privacy',
                'meta_sharing',
                'meta_license_cc0',
                'meta_license'
            ]
        }),
        ('Date information', {
            'fields': ['registration_date'],
            'classes': ['collapse']
        }),
        ('Registration Complete', {
            'fields': ['registration_complete', 'metadata_complete', 'desk_contact']
        })
    ]

    list_display_links = ['link']
    list_display = (
        'link',
        'id',
        'contact_name',
        'contact_email',
        'active_provider',
        'provider_short_name',
        'provider_long_name',
        'registration_date',
        'base_url',
        'registration_complete',
        'metadata_complete',
        'desk_contact'
    )

    list_filter = ['registration_date']
    search_fields = ['provider_long_name']

    list_editable = ['provider_long_name', 'provider_short_name', 'active_provider', 'desk_contact']

    def __unicode__(self):
        return "Registration"

admin.site.register(RegistrationInfo, RegistrationAdmin)
