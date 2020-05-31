# forum-django

[![Build Status](https://travis-ci.org/karolyi/forum-django.svg?branch=development)](https://travis-ci.org/karolyi/forum-django)
[![Coverage Status](https://coveralls.io/repos/github/karolyi/forum-django/badge.svg?branch=development)](https://coveralls.io/github/karolyi/forum-django?branch=development)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/ca3d90d5cb0e43e381274d6f48463a97/badge.svg)](https://www.quantifiedcode.com/app/project/ca3d90d5cb0e43e381274d6f48463a97)

This project is a rewrite of my old, PHP-MySQL based forum from 2004, [https://crxforum.ksol.io](https://crxforum.ksol.io).

I'm rewriting the whole thing in Django, using jQuery/ES6/Webpack, and also adding new features to it over time.

In case of using MariaDB, this project needs MariaDB >= 10.4, as the [BLOB unique indexes weren't available before that](https://mariadb.com/kb/en/blob/#indexing).
