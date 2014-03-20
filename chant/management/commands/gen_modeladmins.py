from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import models as django_models

# https://github.com/bancek/django-autoadmin/blob/master/autoadmin/management/commands/gen_modeladmins.py


class Command(BaseCommand):
    help = ('Generates Django Model Admins code. For example:\n'
            'python manage.py gen_modeladmins app')
    args = '[app_name]'

    requires_model_validation = False

    def handle(self, *args, **options):
        try:
            app_name = args[0]
        except:
            raise CommandError('Invalid arguments, must provide: %s' % self.args)

        def col(model, field):
            if isinstance(field, django_models.ForeignKey):
                return """uni_fk_tr_10('%s')""" % field.name

            return """uni_tr_10('%s')""" % field.name

        print """\
# -*- coding: utf-8 -*-
from django.contrib import admin
#from django.utils.text import truncate_words
from django.core import urlresolvers
from django.utils.html import escape

try:
    from import_export.admin import ImportExportModelAdmin
    AdminClass = ImportExportModelAdmin
except:
    AdminClass = admin.ModelAdmin


from django.utils.text import Truncator
truncate_words = lambda value, length: Truncator(value).words(length, html=True)

from %s.models import *

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
            url_name = 'admin:%%s_%%s_change' %% (f._meta.app_label, f._meta.module_name)
            url = urlresolvers.reverse(url_name, args=(f.pk,))
        except Exception as e:
            url = ''

        return u'<a href="%%s">%%s</a>' %% (url, name)

    func.allow_tags = True
    func.short_description = fnparts[-1]
    
    if order_field is not False:
        func.admin_order_field = order_field or field_name
    
    return func
""" % app_name

        is_text = lambda x: isinstance(x, (django_models.CharField,
                                           django_models.TextField))
        is_fk = lambda x: isinstance(x, django_models.ForeignKey)

        quotes = lambda x: u"'%s'" % x

        for model in django_models.get_models():
            if model._meta.app_label == app_name:
                searchable = [f.name for f in model._meta.fields if is_text(f)]
                cols = [col(model, f) for f in model._meta.fields]
                fkeys = [f.name for f in model._meta.fields if is_fk(f)]

                print """\
class %(model)sAdmin(AdminClass):
    search_fields = [%(searchable)s]
    list_display = [%(cols)s]
    raw_id_fields = [%(fkeys)s]

admin.site.register(%(model)s, %(model)sAdmin)
""" % {
                    'model': model.__name__,
                    'searchable': ', '.join(map(quotes, searchable)),
                    'cols': ', '.join(cols),
                    'fkeys': ', '.join(map(quotes, fkeys)),
                    }