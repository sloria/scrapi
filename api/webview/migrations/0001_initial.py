# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=255)),
                ('docID', models.TextField()),
                ('providerUpdatedDateTime', models.DateTimeField(null=True)),
                ('raw', django_pgjson.fields.JsonField()),
                ('normalized', django_pgjson.fields.JsonField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HarvesterResponse',
            fields=[
                ('key', models.TextField(serialize=False, primary_key=True)),
                ('method', models.CharField(max_length=8)),
                ('url', models.TextField()),
                ('ok', models.NullBooleanField()),
                ('content', models.BinaryField(null=True)),
                ('encoding', models.TextField(null=True)),
                ('headers_str', models.TextField(null=True)),
                ('status_code', models.IntegerField(null=True)),
                ('time_made', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('reconstructed_name', models.CharField(max_length=255)),
                ('institution', models.CharField(max_length=255, null=True)),
                ('id_osf', models.CharField(max_length=10, null=True)),
                ('id_orcid', models.CharField(max_length=100, null=True)),
                ('id_email', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('established', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PushedData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jsonData', django_pgjson.fields.JsonField(null=True)),
                ('collectionDateTime', models.DateTimeField(auto_now_add=True)),
                ('source', models.ForeignKey(related_name='data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Data Object',
            },
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=500)),
                ('status', django_pgjson.fields.JsonField(null=True)),
                ('response', models.ForeignKey(related_name='response', to='webview.HarvesterResponse', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='contributors',
            field=models.ManyToManyField(related_name='documents', to='webview.Person'),
        ),
        migrations.AddField(
            model_name='document',
            name='urls',
            field=models.ManyToManyField(related_name='urls', to='webview.URL'),
        ),
    ]
