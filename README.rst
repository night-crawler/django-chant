``django-chant`` is a chat via pure websockets and tornado.

At this moment it's not a standalone chat application, but it can easily be extracted:
use `chant` folder in your project.

DEMO: http://django-chant.force.fm/
(use google openid auth)

Features
========

* rooms
* typing notification
* rate limits
* max connections limit
* authentication
* gravatar icons
* markdown support


Requirements
============

* django
* tornado
* bootstrap3
* jquery
* jquery mustache
* moment js
* jquery-slimscroll
* bootstrap


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


MAX_CONNECTIONS::

    CHANT_MAX_CONNECTIONS (int)

