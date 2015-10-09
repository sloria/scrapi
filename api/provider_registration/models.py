import datetime

from django.db import models
from django.utils import timezone


class RegistrationInfo(models.Model):
    link = 'Edit'

    # Contact Information
    contact_email = models.EmailField()
    contact_name = models.CharField(max_length=100)

    # Terms of Service and Metadata Permissions Questions
    meta_tos = models.BooleanField(default=False)
    meta_rights = models.BooleanField(default=False)
    meta_privacy = models.BooleanField(default=False)
    meta_sharing = models.BooleanField(default=False)
    meta_license_cc0 = models.BooleanField(default=False)
    meta_license = models.CharField(max_length=100, default='None')

    #Provider Information
    base_url = models.URLField()
    description = models.TextField()
    oai_provider = models.BooleanField(default=False)
    api_docs = models.URLField(blank=True, default='')
    provider_long_name = models.CharField(max_length=100)
    per_request_rate_limit = models.PositiveSmallIntegerField(default=0)
    rate_limit = models.CharField(max_length=100, blank=True, default='')
    provider_short_name = models.CharField(max_length=50, blank=True, default='')

    # Harvester Information
    property_list = models.TextField(default='None')
    active_provider = models.BooleanField(default=False)
    approved_sets = models.TextField(blank=True, default='')

    # Added automatically
    registration_date = models.DateTimeField('date registered')

    # Registation or metadata complete?
    registration_complete = models.BooleanField(default=False)
    metadata_complete = models.BooleanField(default=False)
    desk_contact = models.BooleanField(default=False)

    def __unicode__(self):
        return self.provider_long_name

    def was_registered_recently(self, days=1):
        now = timezone.now()
        return now - datetime.timedelta(days) <= self.registration_date <= now

    was_registered_recently.boolean = True
    was_registered_recently.admin_order_field = 'registration_date'
    was_registered_recently.short_description = 'Registered recently?'

    class Meta:
        verbose_name = 'Registration'
