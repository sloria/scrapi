# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_email', models.EmailField(max_length=75)),
                ('contact_name', models.CharField(max_length=100)),
                ('meta_tos', models.BooleanField(default=False)),
                ('meta_rights', models.BooleanField(default=False)),
                ('meta_privacy', models.BooleanField(default=False)),
                ('meta_sharing', models.BooleanField(default=False)),
                ('meta_license_cc0', models.BooleanField(default=False)),
                ('meta_license', models.CharField(default=b'None', max_length=100)),
                ('base_url', models.URLField()),
                ('description', models.TextField()),
                ('oai_provider', models.BooleanField(default=False)),
                ('api_docs', models.URLField(default=b'', blank=True)),
                ('provider_long_name', models.CharField(max_length=100)),
                ('per_request_rate_limit', models.PositiveSmallIntegerField(default=0)),
                ('rate_limit', models.CharField(default=b'', max_length=100, blank=True)),
                ('provider_short_name', models.CharField(default=b'', max_length=50, blank=True)),
                ('property_list', models.TextField(default=b'None')),
                ('active_provider', models.BooleanField(default=False)),
                ('approved_sets', models.TextField(default=b'', blank=True)),
                ('registration_date', models.DateTimeField(verbose_name=b'date registered')),
            ],
            options={
                'verbose_name': 'Registration',
            },
            bases=(models.Model,),
        ),
    ]
