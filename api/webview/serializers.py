from rest_framework import serializers

from django.contrib.auth.models import User
from api.webview.validators import JsonSchema
from api.webview.models import Document, PushedData
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('id', 'providerUpdatedDateTime', 'source', 'docID', 'raw', 'normalized')


class PushedDataSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    source = serializers.ReadOnlyField(source='source.username')

    class Meta:
        model = PushedData
        fields = ('id', 'collectionDateTime', 'source', 'jsonData')
        list_serializer_class = BulkListSerializer

        validators = [
            JsonSchema()
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    data = serializers.HyperlinkedRelatedField(many=True, view_name='data-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'data')
