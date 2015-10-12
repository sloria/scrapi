from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django_pgjson.fields import JsonField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


class Person(models.Model):
    name = models.CharField(max_length=255)
    reconstructed_name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255, null=True)
    id_osf = models.CharField(max_length=10, null=True)
    id_orcid = models.CharField(max_length=100, null=True)
    id_email = models.CharField(max_length=255, null=True)


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


class Provider(models.Model):
    user = models.OneToOneField(User)
    established = models.BooleanField(default=False)


class PushedData(models.Model):
    jsonData = JsonField(null=True)
    source = models.ForeignKey('auth.User', related_name='data')
    collectionDateTime = models.DateTimeField(auto_now_add=True)

    @property
    def established(self):
        return self.source.provider.established

    @classmethod
    def fetch_established(cls):
        return cls.objects.all().filter(source__provider__established=True)

    class Meta:
        verbose_name = 'Data Object'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
