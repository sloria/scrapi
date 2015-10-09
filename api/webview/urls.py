from django.conf.urls import url
from api.webview import views

urlpatterns = [
    url(r'^documents/$', views.DocumentList.as_view()),
    url(r'^documents/(?P<source>\w+)/$', views.DocumentsFromSource.as_view(), name='source'),
    url(r'^documents/(?P<source>[a-z]+)/(?P<docID>(.*))/$', views.document_detail, name='document_detail'),
    url(r'^posted/', views.DataList.as_view()),
    url(r'^established/$', views.EstablishedDataList.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', views.DataDetail.as_view(), name='data-detail'),
    url(r'^get-api-key/$', views.render_api_form, name='get-api-key'),
    url(r'^help/$', views.render_api_help, name='help'),
]
