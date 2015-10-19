from django.db import models
from django_pgjson.fields import JsonField


class Person(models.Model):
    raw_name = models.CharField(max_length=255)  # source name we got
    name = models.CharField(max_length=255)  # reconstructed - given+add+fam
    family_name = models.CharField(max_length=255, null=True)
    given_name = models.CharField(max_length=255, null=True)
    additional_name = models.CharField(max_length=255, null=True)
    institution = models.CharField(max_length=255, null=True)
    id_osf = models.CharField(max_length=10, null=True)
    id_orcid = models.CharField(max_length=100, null=True)
    id_email = models.CharField(max_length=255, null=True)
    raw_orcid = JsonField(null=True)


class HarvesterResponse(models.Model):

    key = models.TextField(primary_key=True)

    method = models.CharField(max_length=8)
    url = models.TextField()

    # Raw request data
    ok = models.NullBooleanField(null=True)
    content = models.BinaryField(null=True)
    encoding = models.TextField(null=True)
    headers_str = models.TextField(null=True)
    status_code = models.IntegerField(null=True)
    time_made = models.DateTimeField(auto_now=True)


class URL(models.Model):
    url = models.CharField(max_length=500)
    status = JsonField(null=True)
    response = models.ForeignKey(HarvesterResponse, related_name='response', null=True)


class Document(models.Model):
    source = models.CharField(max_length=255)
    docID = models.TextField()

    providerUpdatedDateTime = models.DateTimeField(null=True)

    raw = JsonField()
    normalized = JsonField(null=True)

    contributors = models.ManyToManyField(Person, related_name='documents')
    urls = models.ManyToManyField(URL, related_name='urls')
