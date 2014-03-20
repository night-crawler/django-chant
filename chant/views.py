# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template.context import RequestContext, Context
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from models import Room, RoomSubscriber
from forms import RoomEditForm, SubscriberEditForm
from django.db.models import Q


@login_required
def list_rooms(request):
    user = request.user
    c = Context({'user': user})
    rooms = Room.objects.filter(Q(user=user) | Q(subscribers__in=[user])).distinct().prefetch_related('subscribers')
    c['rooms'] = rooms
    return render_to_response('chant/list_rooms.html', c, context_instance=RequestContext(request))


@login_required
def edit_room(request, room_id=None):
    user = request.user
    c = Context({'user': user})

    instance = get_object_or_404(Room, pk=room_id, user=user) if room_id else Room(user=user)
    form = RoomEditForm(request.POST or None, instance=instance)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('list_rooms'))

    c['form'] = form

    return render_to_response('chant/edit_room.html', c, context_instance=RequestContext(request))


@login_required
def delete_room(request, room_id):
    user = request.user
    instance = get_object_or_404(Room, pk=room_id, user=user)
    instance.delete()
    return HttpResponseRedirect(reverse('list_rooms'))


@login_required
def add_subscriber(request, room_id):
    user = request.user
    c = Context({'user': user})

    rooms_qs = Room.objects.filter(user=user)
    room = get_object_or_404(rooms_qs, pk=room_id)

    instance = RoomSubscriber(room=room)
    form = SubscriberEditForm(request.POST or None, instance=instance)

    if form.is_valid():
        try:
            form.save()
        except:
            pass
        return HttpResponseRedirect(reverse('list_rooms'))

    c['form'] = form
    c['room'] = room
    return render_to_response('chant/add_subscriber.html', c, context_instance=RequestContext(request))


@login_required
def delete_subscriber(request, room_id, user_id):
    user = request.user
    instance = get_object_or_404(RoomSubscriber, room=room_id, user=user_id, room__user=user)
    instance.delete()
    return HttpResponseRedirect(reverse('list_rooms'))