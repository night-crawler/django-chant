# -*- coding: utf-8 -*-
from django.contrib import admin
#from django.utils.text import truncate_words
from django.core import urlresolvers
from django.utils.html import escape

try:
    from import_export.admin import ImportExportModelAdmin
    AdminClass = admin.ModelAdmin
except:
    AdminClass = admin.ModelAdmin


from django.utils.text import Truncator
truncate_words = lambda value, length: Truncator(value).words(length, html=True)

from chant.models import *

def uni_tr_10(field_name):
    def func(obj):
        return truncate_words(unicode(getattr(obj, field_name)), 10)

    func.short_description = field_name
    func.admin_order_field = field_name

    return func

def uni_fk_tr_10(field_name, order_field=None):
    fnparts = field_name.split('__')

    def func(obj):
        f = getattr(obj, fnparts[0])
        for part in fnparts[1:]:
            f = getattr(f, part)
        name = escape(truncate_words(unicode(f), 10))

        try:
            url_name = 'admin:%s_%s_change' % (f._meta.app_label, f._meta.module_name)
            url = urlresolvers.reverse(url_name, args=(f.pk,))
        except Exception as e:
            url = ''

        return u'<a href="%s">%s</a>' % (url, name)

    func.allow_tags = True
    func.short_description = fnparts[-1]
    
    if order_field is not False:
        func.admin_order_field = order_field or field_name
    
    return func

class RoomAdmin(AdminClass):
    search_fields = ['name', 'description', 'topic']
    list_display = [uni_tr_10('id'), uni_tr_10('created_at'), uni_tr_10('updated_at'), uni_fk_tr_10('user'), uni_tr_10('name'), uni_tr_10('description'), uni_tr_10('topic'), uni_fk_tr_10('last_message')]
    raw_id_fields = ['user', 'last_message']

admin.site.register(Room, RoomAdmin)

class RoomSubscriberAdmin(AdminClass):
    search_fields = []
    list_display = [uni_tr_10('id'), uni_tr_10('created_at'), uni_tr_10('updated_at'), uni_fk_tr_10('room'), uni_fk_tr_10('user')]
    raw_id_fields = ['room', 'user']

admin.site.register(RoomSubscriber, RoomSubscriberAdmin)

class MessageAdmin(AdminClass):
    search_fields = ['username', 'text', 'html']
    list_display = [uni_tr_10('id'), uni_tr_10('created_at'), uni_tr_10('updated_at'), uni_fk_tr_10('user'), uni_tr_10('username'), uni_fk_tr_10('room'), uni_tr_10('text'), uni_tr_10('html')]
    raw_id_fields = ['user', 'room']

admin.site.register(Message, MessageAdmin)

