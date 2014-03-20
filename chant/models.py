# -*- coding: utf-8 -*-
from django.utils.functional import cached_property
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.utils.timezone import now
import markdown


class TimeMixIn(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Last update'), auto_now=True)

    class Meta:
        abstract = True


class Room(TimeMixIn, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('Room created by'), related_name='room_users')
    name = models.CharField(_('Name'), max_length=64, unique=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RoomSubscriber', blank=True, null=True, verbose_name=_('Subscribers'), related_name='room_subscribers')

    topic = models.CharField(_('Room topic'), max_length=255, blank=True, null=True)

    last_message = models.ForeignKey('Message', blank=True, null=True, verbose_name=_('Last message'), related_name='+')

    def __unicode__(self):
        names = [n for n in [self.name, self.topic] if n]
        return u': '.join(names)

    class Meta:
        ordering = ['user', 'name']


class RoomSubscriber(TimeMixIn, models.Model):
    room = models.ForeignKey('Room', verbose_name=_('Room'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))

    class Meta:
        unique_together = (('room', 'user'), )
        ordering = ['room', 'user']


class Message(TimeMixIn, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('User'), on_delete=models.SET_NULL)
    username = models.CharField(_('Username'), max_length=20, blank=True, null=True)
    room = models.ForeignKey(Room, verbose_name=_('Room'), related_name='messages')
    text = models.TextField(_('Text'))
    html = models.TextField(_('Rendered text'), editable=False, blank=True, null=True)

    def render_markdown(self):
        return markdown.markdown(self.text, safe_mode='escape')

    def __unicode__(self):
        return self.text[:64]


def room_post_save(sender, instance, created, **kwargs):
    RoomSubscriber.objects.get_or_create(user=instance.user, room=instance)


def message_post_save(sender, instance, created, **kwargs):
    Room.objects.filter(id=instance.room_id).update(last_message=instance, updated_at=now())


def message_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance.html = instance.render_markdown()


post_save.connect(room_post_save, sender=Room, dispatch_uid='room_post_save')
post_save.connect(message_post_save, sender=Message, dispatch_uid='message_post_save')
pre_save.connect(message_pre_save, sender=Message, dispatch_uid='message_pre_save')