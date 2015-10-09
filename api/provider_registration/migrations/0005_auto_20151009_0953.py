# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('provider_registration', '0004_registrationinfo_desk_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationinfo',
            name='contact_email',
            field=models.EmailField(max_length=254),
        ),
    ]
