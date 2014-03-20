# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


CHANT_URLS = patterns('chant.views',
    url(r'^rooms/$', 'list_rooms', name='list_rooms'),
    url(r'^rooms/edit/(?:(?P<room_id>\d+)/)?$', 'edit_room', name='edit_room'),
    url(r'^rooms/delete/(?P<room_id>\d+)/$', 'delete_room', name='delete_room'),

    url(r'^rooms/(?P<room_id>\d+)/add/subscriber/$', 'add_subscriber', name='add_subscriber'),
    url(r'^rooms/(?P<room_id>\d+)/subscribers/delete/(?P<user_id>\d+)/$', 'delete_subscriber', name='delete_subscriber'),
)

urlpatterns = CHANT_URLS