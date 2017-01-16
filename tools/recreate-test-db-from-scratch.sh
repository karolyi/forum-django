#!/usr/bin/env bash

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)

cd $MY_DIR

if [[ -e $MY_DIR/venv/bin/activate && -z $VIRTUAL_ENV ]]; then
    # Only activate virtualenv if it exists and not activated yet
    source $MY_DIR/venv/bin/activate
fi

mysql -uroot -e 'drop database `test_forum-django2`'
mysql -uroot -e 'create database `test_forum-django2` default character set utf8mb4 default collate utf8mb4_general_ci'

if [[ $1 != 'norecreate' ]]; then
    echo DELETING MIGRATIONS
    find ./ -wholename '*backend/forum/*migrations/*py' -delete
    backend/manage.py makemigrations --settings forum.settings_test_2 forum_account forum_base forum_cdn forum_crowdfunding forum_event forum_messaging forum_poll forum_rating forum_rest_api
    isort ./backend/forum/*/migrations/0001_initial.py
fi
backend/manage.py migrate --settings forum.settings_test_2
if [[ $1 != 'noloaddump' ]]; then
    echo LOADING DUMPS
    backend/manage.py loaddata backend/forum/base/fixtures/*yaml --settings forum.settings_test_2
fi
