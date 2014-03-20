# -*- coding: utf-8 -*-
import json

from threading import Thread
from functools import wraps

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import Application
from tornado import gen

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.conf import settings
from django.contrib import auth
from django.utils.importlib import import_module
from django.utils.functional import Promise
from django.utils.timezone import now

from .models import Message, RoomSubscriber, Room
from .utils import model_to_dict, import_to_python, RateLimiter
from .settings import FORMAT_USER_PATH, MAX_CONNECTIONS, RATE_LIMITS


session_engine = import_module(settings.SESSION_ENGINE)
format_user = import_to_python(FORMAT_USER_PATH)


def run_async(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


class DummyRequest(object):
    pass


class ResponseDict(dict):
    def __init__(self, **kwargs):
        data = kwargs.pop('data', [])
        super(ResponseDict, self).__init__(**kwargs)
        self['timestamp'] = now()
        self['command'] = None
        self['data'] = data


class ErrorResponse(ResponseDict):
    def __init__(self, **kwargs):
        reason = kwargs.pop('reason', None)
        super(ErrorResponse, self).__init__(**kwargs)
        self['command'] = 'error'
        self['result'] = 'error'
        self['reason'] = reason


class CommandNotAllowedResponse(ErrorResponse):
    def __init__(self, **kwargs):
        super(CommandNotAllowedResponse, self).__init__(reason='not_allowed', **kwargs)


class RateLimitExceededResponse(ErrorResponse):
    def __init__(self, **kwargs):
        super(RateLimitExceededResponse, self).__init__(reason='rate_limit_exceeded', **kwargs)


class ServerFullResponse(ErrorResponse):
    def __init__(self, **kwargs):
        super(ServerFullResponse, self).__init__(reason='full', **kwargs)


class UnauthenticatedResponse(ErrorResponse):
    def __init__(self, **kwargs):
        super(UnauthenticatedResponse, self).__init__(reason='unauthenticated', **kwargs)


class SuccessResponse(ResponseDict):
    def __init__(self, **kwargs):
        super(SuccessResponse, self).__init__(**kwargs)
        self['result'] = 'success'


class RoomsResponse(SuccessResponse):
    def __init__(self, **kwargs):
        super(RoomsResponse, self).__init__(**kwargs)
        self['command'] = 'rooms'


class AuthResponseAccept(SuccessResponse):
    def __init__(self, **kwargs):
        super(AuthResponseAccept, self).__init__(**kwargs)
        self['command'] = 'authenticate'


class AuthResponseDecline(ErrorResponse):
    def __init__(self, **kwargs):
        super(AuthResponseDecline, self).__init__(**kwargs)
        self['command'] = 'authenticate'
        self['result'] = 'auth_declined'


class MessageResponse(SuccessResponse):
    def __init__(self, **kwargs):
        message = kwargs.pop('message')
        super(MessageResponse, self).__init__(**kwargs)
        self['command'] = 'post'

        message_dict = model_to_dict(message)
        message_dict['user'] = format_user(message.user)

        self['data'] = message_dict


class HistoryResponse(SuccessResponse):
    def __init__(self, **kwargs):
        room = kwargs.pop('room')
        messages_qs = kwargs.pop('messages')
        super(HistoryResponse, self).__init__(**kwargs)
        self['command'] = 'history'

        messages = []
        for m in messages_qs:
            message_dict = model_to_dict(m)
            message_dict['user'] = format_user(m.user)
            messages.append(message_dict)

        self['data'] = {'room': room, 'messages': messages}


class TypingResponse(SuccessResponse):
    def __init__(self, **kwargs):
        super(TypingResponse, self).__init__(**kwargs)
        self['command'] = 'typing'


class MessagesHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.room_id = None
        self.session_key = None
        self.user = None
        self.request_counter = 0
        self.allowed_commands = ['authenticate', 'post', 'typing', 'history', 'rooms']

        self.rate_blocks = {k: RateLimiter(**v) for k, v in RATE_LIMITS.items()}

        super(MessagesHandler, self).__init__(*args, **kwargs)

    def open(self):
        if len(self.application.connections) > MAX_CONNECTIONS:
            self.json_response(ServerFullResponse())
            self.close()

        self.application.connections['anonymous'].add(self)

    def on_close(self):
        connections = self.application.connections
        try:
            if self.user and self.user.is_authenticated():
                connections[self.user.id].remove(self)
            else:
                connections['anonymous'].remove(self)
        except KeyError:
            pass

    def json_response(self, data):
        if self.ws_connection is None:
            return False

        self.write_message(json.dumps(data, cls=DjangoJSONEncoder))
        return True

    def error_response(self, msg):
        msg = unicode(msg) if isinstance(msg, (basestring, Promise)) else msg
        self.json_response(ErrorResponse(reason=msg))

    @gen.coroutine
    def on_message(self, client_data):
        msg = json.loads(client_data)
        request = msg.get('request')
        data = msg.get('data')

        if not request in self.allowed_commands:
            self.json_response(CommandNotAllowedResponse())

        if self.rate_blocks['on_message']():
            self.json_response(RateLimitExceededResponse())
            return

        request_rate_limiter = self.rate_blocks[request]
        if request_rate_limiter():
            self.json_response(RateLimitExceededResponse())
            return

        method_name = 'chant_%s' % request
        method = getattr(self, method_name)
        result = method(data)

    def get_current_user(self):
        session = session_engine.SessionStore(self.session_key)
        r = DummyRequest()
        r.session = session
        self.user = auth.get_user(r)
        return self.user

    def subscribed_rooms(self, values=False):
        subscribed_qs = RoomSubscriber.objects\
            .filter(user=self.user)\
            .select_related('room', 'user')
        if not values:
            return subscribed_qs

        rooms = []
        for s in subscribed_qs:
            room_dict = model_to_dict(s.room)
            room_dict['subscriber'] = model_to_dict(s)
            rooms.append(room_dict)

        return rooms

    @run_async
    def chant_authenticate(self, session_key, callback=None):
        self.session_key = session_key
        user = self.get_current_user()

        connections = self.application.connections
        # TODO: move other anon connections to authenticated by stores same session_key
        if self.user.is_authenticated():
            connections.setdefault(user.id, set())
            connections['anonymous'].remove(self)
            connections[user.id].add(self)
            self.json_response(AuthResponseAccept())
        else:
            self.json_response(AuthResponseDecline())

    @run_async
    def chant_post(self, data, callback=None):
        room_id, message = data.get('room'), data.get('message')
        if not room_id or not message:
            return self.json_response(UnauthenticatedResponse())

        lookup = (Q(user=self.user) | Q(subscribers__in=[self.user])) & Q(pk=room_id)
        room = Room.objects.filter(lookup).prefetch_related('subscribers')[0]

        message_dict = {'text': message, 'room': room}
        if self.user and self.user.is_authenticated():
            message_dict['user'] = self.user
            message_dict['username'] = self.user.username

        message = Message(**message_dict)
        message.save()

        subscribers_set = room.subscribers.all().values_list('id', flat=True)
        for uid, user_connections in self.application.connections.items():
            if not uid in subscribers_set:
                continue

            for conn in user_connections:
                conn.json_response(MessageResponse(message=message))

    @run_async
    def chant_rooms(self, data, callback=None):
        if not self.user or not self.user.is_authenticated():
            return self.json_response(UnauthenticatedResponse())

        rooms = self.subscribed_rooms(values=True)
        self.json_response(RoomsResponse(data=rooms))

    @run_async
    def chant_typing(self, data, callback=None):
        if not self.user or not self.user.is_authenticated():
            return self.json_response(UnauthenticatedResponse())

        room = data.get('room')
        room_subscribers = RoomSubscriber.objects.filter(
            room=room,
            room__subscribers__in=[self.user]
        ).values_list('user', flat=True)  # .exclude(pk=self.user.id)

        user_repr = format_user(self.user)
        for uid in room_subscribers:
            for conn in self.application.connections.get(uid, set()):
                conn.json_response(TypingResponse(data={'user': user_repr, 'room': room}))

    @run_async
    def chant_history(self, data, callback=None):
        if not self.user or not self.user.is_authenticated():
            return self.json_response(UnauthenticatedResponse())

        limit = data['count']
        if limit > 100:
            limit = 100

        filters = Q(room__subscribers__in=[self.user]) & Q(room=data['room'])
        if data['least_id']:
            filters &= Q(pk__lt=data['least_id'])

        messages_qs = Message.objects.filter(filters).select_related('user').order_by('-id')[:limit]
        self.json_response(HistoryResponse(room=data['room'], messages=messages_qs))


class ChantApplication(Application):
    def __init__(self):
        self.rooms = {}
        self.connections = {
            'anonymous': set()
        }

        handlers = (
            (r'/', MessagesHandler),
        )
        Application.__init__(self, handlers)


application = ChantApplication()

if __name__ == "__main__":
    application.listen(8888, '0.0.0.0')
    IOLoop.instance().start()