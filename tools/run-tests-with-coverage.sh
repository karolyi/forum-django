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
EXITCODE_TESTS=$?

coverage html  --omit='*/migrations/*'

# Start the http server inly when we're not on travis
if [[ -z "$TRAVIS" ]]; then
    python3 -m http.server
else
    exit $EXITCODE_TESTS
fi
