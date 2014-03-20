# -*- coding: utf-8 -*-
from django import forms
from django.db.models.query_utils import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from models import Room, RoomSubscriber


class RoomEditForm(forms.ModelForm):

    class Meta:
        model = Room
        exclude = ('user', 'last_message', 'subscribers')


class SubscriberEditForm(forms.ModelForm):
    user = forms.CharField(label=_('Email or username'))

    def clean_user(self):
        data = self.cleaned_data['user']
        try:
            user = User.objects.get(Q(username=data) | Q(email=data))
        except:
            raise forms.ValidationError(_('Enter a valid username or email'))

        return user

    class Meta:
        model = RoomSubscriber
        exclude = ('room', )
