#!/usr/bin/env sh

test -p /tmp/forum-test.master-fifo.sock && echo l >/tmp/forum-test.master-fifo.sock
