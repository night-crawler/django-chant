# -*- coding: utf-8 -*-
import time

from collections import deque
from hashlib import md5
from .settings import AVATAR_HEIGHT, AVATAR_WIDTH, GRAVATAR_DEFAULT


def import_to_python(import_str):
    """Given a string 'a.b.c' return object c from a.b module."""
    mod_name, obj_name = import_str.rsplit('.', 1)
    mod = __import__(mod_name, {}, {}, [''])
    #print mod_name, obj_name, mod, dir(mod)
    obj = getattr(mod, obj_name)
    return obj


def model_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    from django.db.models.fields.related import ManyToManyField
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.virtual_fields + opts.many_to_many:
        # if not getattr(f, 'editable', False):
        #     continue
        if fields and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primary key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[f.name] = []
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def gravatar_url(email, width, height, gravatar_default):
    digest = md5(email.lower()).hexdigest()
    size = max(width, height)
    url = '//www.gravatar.com/avatar/%s?size=%s&default=%s' % (digest, size, gravatar_default)
    return url


def format_user(user):
    user_dict = model_to_dict(user, fields=['id', 'username', 'name', 'first_name', 'last_name'])
    user_dict.update({
        'avatar': gravatar_url(user.email, AVATAR_WIDTH, AVATAR_HEIGHT, GRAVATAR_DEFAULT)
    })

    return user_dict


class RateLimiter:
    def __init__(self, max_rate=5, time_unit=1):
        self.time_unit = time_unit
        self.deque = deque(maxlen=max_rate)

    def __call__(self):
        current_time = time.time()

        if self.deque.maxlen == len(self.deque):
            if current_time - self.deque[0] > self.time_unit:
                self.deque.append(current_time)
                return False
            else:
                return True

        self.deque.append(current_time)
        return False