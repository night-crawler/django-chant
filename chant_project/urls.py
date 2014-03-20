from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^chant/', include('chant.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('common.urls')),

    url(r'social/', include('social.apps.django_app.urls', namespace='social'))
)
