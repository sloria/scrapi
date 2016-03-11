from rest_framework import serializers

from api.webview.models import Document, LastHarvest


class DocumentSerializer(serializers.ModelSerializer):
    raw = serializers.JSONField()
    normalized = serializers.JSONField()

    class Meta:
        model = Document
        fields = ('key', 'providerUpdatedDateTime', 'source', 'docID', 'raw', 'normalized')


class LastHarvestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LastHarvest
        fields = ('source', 'last_harvest')
