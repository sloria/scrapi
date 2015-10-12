from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.webview.urls')),
    url(r'^registration/', include('api.provider_registration.urls', namespace="provider_registration"))
]
