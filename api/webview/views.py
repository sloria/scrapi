from dateutil.parser import parse

from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.models import User

from api.webview.models import Document, PushedData
from api.webview.permissions import IsOwnerOrReadOnly
from api.webview.serializers import DocumentSerializer, PushedDataSerializer, UserSerializer


class DocumentList(generics.ListCreateAPIView):
    """
    List all documents in the SHARE API
    """
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        serializer.save(source=self.request.user)

    def get_queryset(self):
        """ Return all documents
        """
        return Document.objects.all()


class DocumentsFromSource(generics.ListCreateAPIView):
    """
    List all documents from a particular source
    """
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        serializer.save(source=self.request.user)

    def get_queryset(self):
        """ Return queryset based on source
        """
        return Document.objects.filter(source=self.kwargs['source'])


@api_view(['GET'])
@xframe_options_exempt
def document_detail(request, source, docID):
    """
    Retrieve one particular document.
    """
    try:
        all_sources = Document.objects.filter(source=source)
        document = all_sources.get(docID=docID)
    except Document.DoesNotExist:
        return Response(status=404)

    serializer = DocumentSerializer(document)
    return Response(serializer.data)


class DataList(ListBulkCreateUpdateDestroyAPIView):
    """
    List all pushed data, or push to the API
    """
    serializer_class = PushedDataSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(source=self.request.user)

    def get_queryset(self):
        """ Return queryset based on from and to kwargs
        """
        filter = {}
        queryset = PushedData.objects.all()

        from_date = self.request.QUERY_PARAMS.get('from')
        to_date = self.request.QUERY_PARAMS.get('to')

        if from_date:
            filter['collectionDateTime__gte'] = parse(from_date)

        if to_date:
            filter['collectionDateTime__lte'] = parse(to_date)

        queryset = queryset.filter(**filter)

        return queryset


class EstablishedDataList(ListBulkCreateUpdateDestroyAPIView):
    """
    List all pushed data that comes from an established provider
    Example query: pushed_data/established?from=2015-03-16&to=2015-04-06
    """
    serializer_class = PushedDataSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(source=self.request.user)

    def get_queryset(self):
        queryset = PushedData.fetch_established()
        filter = {}

        from_date = self.request.QUERY_PARAMS.get('from')
        to_date = self.request.QUERY_PARAMS.get('to')

        if from_date:
            filter['collectionDateTime__gte'] = parse(from_date)

        if to_date:
            filter['collectionDateTime__lte'] = parse(to_date)

        queryset = queryset.filter(**filter)

        return queryset


class DataDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete pushed data
    """
    queryset = PushedData.objects.all()
    serializer_class = PushedDataSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def render_api_form(request):
    token = request.user.auth_token
    return render(
        request,
        'rest_framework/get_api_key.html',
        {'auth_token': token}
    )


@xframe_options_exempt
def render_api_help(request):
    return render(
        request,
        'rest_framework/api_docs.html',
    )
