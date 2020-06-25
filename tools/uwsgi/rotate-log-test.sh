#!/usr/bin/env sh

if [ -p /tmp/forum-test.master-fifo.sock ]; then
    echo l >/tmp/forum-test.master-fifo.sock
    logger -t forum-test Uwsgi FIFO socket rotate command sent.
fi
