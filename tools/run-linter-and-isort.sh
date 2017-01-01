#!/usr/bin/env bash

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)

cd $MY_DIR

if [[ -e $MY_DIR/venv/bin/activate && -z $VIRTUAL_ENV ]]; then
    # Only activate virtualenv if it exists and not activated yet
    source $MY_DIR/venv/bin/activate
fi

isort -c --skip-glob=node_modules --skip-glob=venv
EXITCODE_ISORT=$?
if [[ $EXITCODE_ISORT -ne 0 ]]; then
    # Isort failed
    if [[ -z "$TRAVIS" ]]; then
        echo ISORT FAILED: $EXITCODE_ISORT
    fi
    exit $EXITCODE_ISORT
fi

flake8 --exclude='*/migrations/*' backend/
EXITCODE_LINTER=$?
if [[ $EXITCODE_LINTER -ne 0 ]]; then
    # Linter failed
    if [[ -z "$TRAVIS" ]]; then
        echo LINTER FAILED: $EXITCODE_LINTER
    fi
    exit $EXITCODE_LINTER
fi

