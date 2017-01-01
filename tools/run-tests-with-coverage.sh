#!/usr/bin/env bash

if [ -n "$(type -t deactivate)" ] && [ "$(type -t deactivate)" = function ]; then
    # deactivate the virtualenv if activated
    deactivate
fi

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)

cd $MY_DIR

source $MY_DIR/venv/bin/activate

export PATH=$PATH:/bin/:/usr/bin
rm -rf htmlcov

coverage run --source 'backend/' backend/manage.py test forum --keepdb -v 2
coverage html  --omit='*/migrations/*'
python3 -m http.server
