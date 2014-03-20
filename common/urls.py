# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('common.views',
    url(r'^$', 'home', name='home'),
    url(r'^signup-email/', 'signup_email'),
    url(r'^email-sent/', 'validation_sent'),
    url(r'^login/$', 'home'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^done/$', 'done', name='done'),
    url(r'^email/$', 'require_email', name='require_email'),    
)