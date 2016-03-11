from django.conf.urls import url, include
from api.webview import views

urlpatterns = [
    url(r'^(documents/){1}(from=((?P<from>(\d{4}-\d{2}-\d{2}){0,1}))&until=((?P<until>\d{4}-\d{2}-\d{2}){0,1})){0,1}/{0,1}$', views.DocumentList.as_view()),
    url(r'^get-api-key/$', views.DocumentList.as_view(), name='get-api-key'),
    url(r'^documents/status', views.status, name='status'),
    url(r'^documents/(?P<source>\w+)/$', views.DocumentsFromSource.as_view(), name='source'),
    url(r'^documents/(?P<source>[a-z]+)/(?P<docID>(.*))/$', views.document_detail, name='document_detail'),
    url(r'^institutions', views.institutions, name='institutions'),
    url(r'^robots\.txt$', include('robots.urls')),
]
