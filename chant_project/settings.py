# -*- coding: utf-8 -*-
import os

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = ROOT_PATH
PROJECT_NAME = os.path.basename(ROOT_PATH)
PROJECT_TEMPLATE_DIR = os.path.join(ROOT_PATH, 'templates')

MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(ROOT_PATH, 'static')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'chant',
    }
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'chant',
    'common',
    'bootstrap3',
    'social.apps.django_app.default',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    #'staticfiles.context_processors.static',
    'social.apps.django_app.context_processors.backends',
)



ROOT_URLCONF = 'chant_project.urls'
WSGI_APPLICATION = 'chant_project.wsgi.application'


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CHANT_RATE_LIMITS = {
    'on_message': {'max_rate': 20, 'time_unit': 1},
    'authenticate': {'max_rate': 1, 'time_unit': 1},
    'post': {'max_rate': 10, 'time_unit': 10},
    'typing': {'max_rate': 10, 'time_unit': 1},
    'history': {'max_rate': 1, 'time_unit': 1},
    'rooms': {'max_rate': 2, 'time_unit': 1}
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '?',
        'USER': '?',
        'PASSWORD': '?',
    }
}

SECRET_KEY = '?'

try:
    from local_settings import *
except ImportError:
    pass

try:
    from social_settings import *
except ImportError:
    pass

try:
    from social_settings_keys import *
except ImportError:
    pass