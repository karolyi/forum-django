#!/usr/bin/env bash

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)

cd $MY_DIR


if [[ -e $MY_DIR/venv/bin/activate && -z $VIRTUAL_ENV ]]; then
    # Only activate virtualenv if it exists and not activated yet
    source $MY_DIR/venv/bin/activate
fi

rm -rf htmlcov

coverage run  --omit='*/migrations/*' --source 'backend/' backend/manage.py test forum --keepdb -v 2
EXITCODE_TESTS=$?

coverage html

# Start the http server inly when we're not on travis
if [[ -z "$TRAVIS" ]]; then
    python3 -m http.server
else
    exit $EXITCODE_TESTS
fi
