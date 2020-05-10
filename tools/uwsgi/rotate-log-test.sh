#!/usr/bin/env sh

if [ -p /tmp/forum-test.master-fifo.sock ]; then
    echo l >/tmp/forum-test.master-fifo.sock
fi
