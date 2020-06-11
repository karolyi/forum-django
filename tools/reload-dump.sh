#!/usr/bin/env bash

mysql -uroot -e 'drop database `forum-django`;create database `forum-django` default character set utf8mb4 default collate utf8mb4_unicode_ci';gunzip -c hondaforum.dump.sql.gz |mysql -uroot forum-django
