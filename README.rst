``django-chant`` is a chat via pure websockets and tornado.

At this moment it's not a standalone chat application, but it can easily be extracted:
use `chant` folder in your project.

DEMO: http://django-chant.force.fm/
(use openid auth only)

Features
========

* rooms
* typing notification
* rate limits
* blacklist
* optional notification (user may cancel chat updates)
* max connections limit
* authentication
* gravatar icons
* markdown support
* sound notification (html5 audio)
* favicon notification

Requirements
============

* django
* tornado
* bootstrap3
* jquery
* jquery mustache
* moment.js
* jquery favico
* jquery-slimscroll
* bootstrap
* html5


Configuration
=============
RATE_LIMIT::

    CHANT_RATE_LIMITS = {
        'on_message': UNLIMITED,
        'authenticate': UNLIMITED,
        'post': UNLIMITED,
        'typing': UNLIMITED,
        'history': UNLIMITED,
        'rooms': UNLIMITED
    }


where `UNLIMITED` is a dict like::

    UNLIMITED = {
        'max_rate': 1,
        'time_unit': 2
    }


MAX_CONNECTIONS::

    CHANT_MAX_CONNECTIONS = 1024

