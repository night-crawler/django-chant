# -*- coding: utf-8 -*-/
from django.conf import settings

FORMAT_USER_PATH = getattr(settings, 'CHANT_FORMAT_USER_PATH', 'chant.utils.format_user')

GRAVATAR_DEFAULT = getattr(settings, 'CHANT_GRAVATAR_DEFAULT', 'identicon')
AVATAR_WIDTH = getattr(settings, 'CHANT_AVATAR_WIDTH', 32)
AVATAR_HEIGHT = getattr(settings, 'CHANT_AVATAR_HEIGHT', 32)

UNLIMITED = {
    'max_rate': 1,
    'time_unit': 2
}

DEFAULT_RATE_LIMITS = {
    'on_message': UNLIMITED,
    'authenticate': UNLIMITED,
    'post': UNLIMITED,
    'typing': UNLIMITED,
    'history': UNLIMITED,
    'rooms': UNLIMITED
}

RATE_LIMITS = getattr(settings, 'CHANT_RATE_LIMITS', DEFAULT_RATE_LIMITS)
for k, v in DEFAULT_RATE_LIMITS.items():
    if k not in RATE_LIMITS:
        RATE_LIMITS[k] = v

MAX_CONNECTIONS = getattr(settings, 'CHANT_MAX_CONNECTIONS', 1024)