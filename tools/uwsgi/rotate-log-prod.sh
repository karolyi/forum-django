#!/usr/bin/env sh

# if [ -p /tmp/forum-prod.master-fifo.sock ]; then
#     echo l >/tmp/forum-prod.master-fifo.sock
#     logger -t forum-prod Uwsgi FIFO socket rotate command sent.
#     touch ~hondaforum-prod/project/forum-django/backend/forum/wsgi.py
# fi
rm /var/log/uwsgi/forum-prod/uwsgi.log
ln /var/log/uwsgi/forum-prod/uwsgi.log.REAL /var/log/uwsgi/forum-prod/uwsgi.log
truncate -s 0 /var/log/uwsgi/forum-prod/uwsgi.log.REAL
