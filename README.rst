``django-chant`` is a chat via pure websockets and tornado.

At this moment it's not a standalone chat application, but it can easily be extracted from project root:
use `chant` folder in your project.

DEMO: http://django-chant.force.fm/
(openid auth only)

Features
========

* rooms
* typing notification
* rate limits
* blacklist
* optional notification (user may cancel chat updates)
* max connections limit
* authentication (via django session)
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


Starting chat daemon
====================
Run::

    ./manage.py startchant 8877


Sample `supervisord` config (i.e., /etc/supervisor/conf.d/django-chant.conf)::

    [program:django-chant]
    process_name=%(program_name)s
    directory=/var/www/django-chant.project/venv/chant_project
    command=/var/www/django-chant.project/venv/bin/python /var/www/django-chant.project/venv/chant_project/manage.py startchant 8877
    autostart=true
    autorestart=true
    redirect_stderr=false

    stdout_logfile=/var/log/chant.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB
    stderr_logfile=/var/log/cat_err.log
    stderr_logfile_maxbytes=1MB
    stderr_logfile_backups=10
    stderr_capture_maxbytes=1MBr


TODO
====

* add manage commands for chat, i.e. `./manage.py chant online`

