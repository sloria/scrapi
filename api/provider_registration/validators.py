import logging

import requests

from lxml import etree
from django import forms
from requests.exceptions import MissingSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IDENTIFY = '?verb=Identify'

NAMESPACES = {'oai': 'http://www.openarchives.org/OAI/2.0/'}


class URLResolves(object):
    def __call__(self, value):
        ''' value is the serialized data to be validated '''
        try:
            data = requests.get(value)
        except (requests.exceptions.ConnectionError, MissingSchema):
            raise forms.ValidationError('URL does not resolve, please enter  a valid URL')
        if data.status_code == 404:
            raise forms.ValidationError('URL does not resolve, please enter  a valid URL')


class ValidOAIURL(object):
    def __call__(self, value):
        ''' value is the serialized data to be validated '''

        url = value + IDENTIFY

        data = requests.get(url)
        if data.status_code == 404:
            raise forms.ValidationError('URL does not resolve, please enter  a valid URL')

        try:
            doc = etree.XML(data.content)
        except etree.XMLSyntaxError:
            raise forms.ValidationError('URL does not return valid XML, please enter a valid OAI-PMH url')

        repository_name = doc.xpath('//oai:repositoryName/node()', namespaces=NAMESPACES) or ['']
        if repository_name[0]:
            logger.info('OAI link valid for: {}'.format(repository_name))
            return True
