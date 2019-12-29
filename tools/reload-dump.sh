#!/usr/bin/env bash

mysql -uroot -e 'drop database `forum-django`;create database `forum-django`';gunzip -c hondaforum.dump.sql.gz |mysql -uroot forum-django
