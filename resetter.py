#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from time import sleep

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
WSGI_FILE = '/var/www/django-chant.project/venv/www/public/index.wsgi'

mtimes = {}
old_mtimes = {}
while True:
    files = ( os.path.join(path, name)
        for path, dirs, files in os.walk(ROOT_PATH)
        for name in files
        if '.py' in name and '#' not in name
        )

    mtimes = { f:os.path.getmtime(f) for f in files }

    for f, mtime in mtimes.items():
        if old_mtimes.get(f, None) != mtime:
            print f, subprocess.call('touch %s' % WSGI_FILE, shell=True)
            break


    old_mtimes = mtimes
    sleep(1)

