from django.conf.urls import include, url

from api.provider_registration import views

urlpatterns = [
    url(r'^/', include([
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register_provider, name='register'),
        url(r'^contact_information/$', views.get_contact_info, name='contact_information'),
        url(r'^provider_information/$', views.save_metadata_render_provider, name='provider_information'),
        url(r'^simple_oai_registration/$', views.redirect_to_simple_oai, name='simple_oai_registration')
    ]))
]
