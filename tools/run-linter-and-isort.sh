#!/usr/bin/env bash

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)

cd $MY_DIR

if [[ -e $MY_DIR/venv/bin/activate && -z $VIRTUAL_ENV ]]; then
    # Only activate virtualenv if it exists and not activated yet
    source $MY_DIR/venv/bin/activate
fi
IFS=$'\n'

if [[ "$1" == '-gn' ]]; then
    FILES=$(git diff --name-status --cached | awk '$1 != "D" { print $2 }')
else
    FILES=$(git ls-files --other --exclude-standard --modified)
fi
PY_FILES=$(echo -n "$FILES"|grep '\.py$')
JS_FILES=$(echo -n "$FILES"|grep '\.js$')

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [[ "$1" == '-n' || "$1" == '-gn' ]]; then
    echo -e "${GREEN}GULP NEW${NC}"
    if [[ "$JS_FILES" == "" ]]; then
        echo No new .js files
        EXITCODE_GULP_LINT=0
    else
        gulp lint -n "$JS_FILES"
        EXITCODE_GULP_LINT=$?
    fi
else
    echo -e "${GREEN}GULP ALL${NC}"
    gulp lint
    EXITCODE_GULP_LINT=$?
fi
if [[ $EXITCODE_GULP_LINT -ne 0 ]]; then
    # Gulp linting (eslint) failed
    if [[ -z "$TRAVIS" ]]; then
        echo GULP LINT FAILED: $EXITCODE_GULP_LINT
    fi
    exit $EXITCODE_GULP_LINT
fi

echo ISORT:
if [[ "$1" == '-u' ]]; then
    echo -e "${GREEN}ISORTING ALL${NC}"
    isort -y --skip-glob=node_modules --skip-glob=venv
    EXITCODE_ISORT=$?
elif [[ "$1" == '-n' || "$1" == '-gn' ]]; then
    echo -e "${GREEN}ISORTING NEW${NC}"
    if [[ "$PY_FILES" == "" ]]; then
        echo No new .py files
        EXITCODE_ISORT=0
    else
        isort -y --skip-glob=node_modules --skip-glob=venv $PY_FILES
        EXITCODE_ISORT=$?
    fi
else
    echo -e "${GREEN}ISORTING CHECK ALL${NC}"
    # check only
    isort -c --skip-glob=node_modules --skip-glob=venv
    EXITCODE_ISORT=$?
fi
echo EXITCODE_ISORT: $EXITCODE_ISORT
if [[ $EXITCODE_ISORT -ne 0 ]]; then
    # Isort failed
    if [[ -z "$TRAVIS" ]]; then
        echo ISORT FAILED: $EXITCODE_ISORT
    fi
    exit $EXITCODE_ISORT
fi

if [[ "$1" == '-n' || "$1" == '-gn' ]]; then
    echo -e "${GREEN}FLAKE8-ING NEW${NC}"
    if [[ "$PY_FILES" == "" ]]; then
        echo No new .py files
        EXITCODE_FLAKE8=0
    else
        flake8 --exclude='*/migrations/*' $PY_FILES
        EXITCODE_FLAKE8=$?
    fi
else
    echo -e "${GREEN}FLAKE8-ING ALL${NC}"
    flake8 --exclude='*/migrations/*' backend/
    EXITCODE_FLAKE8=$?
fi
if [[ $EXITCODE_FLAKE8 -ne 0 ]]; then
    # Linter failed
    if [[ -z "$TRAVIS" ]]; then
        echo LINTER FAILED: $EXITCODE_FLAKE8
    fi
    exit $EXITCODE_FLAKE8
fi

echo LINTING SUCCESS
