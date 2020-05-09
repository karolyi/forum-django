#!/usr/bin/env sh

test -p /tmp/forum-prod.master-fifo.sock && echo l >/tmp/forum-prod.master-fifo.sock
