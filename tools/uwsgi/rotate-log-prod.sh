#!/usr/bin/env sh

if [ -p /tmp/forum-prod.master-fifo.sock ]; then
    echo l >/tmp/forum-prod.master-fifo.sock
    logger -t forum-prod Uwsgi FIFO socket rotate command sent.
    touch ~hondaforum-prod/project/forum-django/backend/forum/wsgi.py
fi
