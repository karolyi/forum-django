#!/usr/bin/env bash

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)
cd $MY_DIR

tools/run-linter-and-isort.sh
EXITCODE_LINTING=$?
if [[ $EXITCODE_LINTING -ne 0 ]]; then
    # Isort failed
    echo ISORT FAILED
    exit $EXITCODE_LINTING
fi

tools/run-tests-with-coverage.sh
