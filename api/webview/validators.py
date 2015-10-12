## custom validators
from __future__ import unicode_literals

import jsonschema
from rest_framework.exceptions import ParseError

from api.webview import schemas


class JsonSchema(object):
    def __call__(self, value):
        json_data = value.get('jsonData')

        try:
            jsonschema.validate(json_data, schemas.share)
        except jsonschema.exceptions.ValidationError as error:
            raise ParseError(detail=error.message)
