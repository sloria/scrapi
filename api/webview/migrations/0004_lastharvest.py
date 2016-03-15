# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webview', '0003_version_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastHarvest',
            fields=[
                ('source', models.TextField(serialize=False, primary_key=True)),
                ('last_harvest', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
