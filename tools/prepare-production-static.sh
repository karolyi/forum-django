#!/usr/bin/env bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# set -x  # Debug

MY_DIR=$(cd $(dirname ${BASH_SOURCE[0]})/..;pwd)
cd $MY_DIR

if [[ -e $MY_DIR/venv/bin/activate && -z $VIRTUAL_ENV ]]; then
    # Only activate virtualenv if it exists and not activated yet
    source $MY_DIR/venv/bin/activate
fi

# At this point we assume that webpack has been already compiled its
# assets with production mode (that is, with uglified JS sources)

echo -e ${GREEN}--- removing static/ content ---${NC}
rm -rf static/*

echo -e ${GREEN}--- running collectstatic ---${NC}
# Delete the old static, collect everything new
# yes yes|./manage.py collectstatic -v0 --clear --noinput
yes yes|backend/manage.py collectstatic -v0 --noinput
EXIT_CODE=$?
if [[ $EXIT_CODE -ne 0 ]]; then
    echo -e ${RED}COLLECTSTATIC EXITED WITH $EXIT_CODE${NC}
    exit $EXIT_CODE
fi

rm -v static.tar.gz

set -e
echo -e ${GREEN}--- compressing static.tar.gz ---${NC}
mv -v static new_static

# No translations yet
# chmod -v 644 frontend/webpack/stats.json backend/switchershop/locale/de/LC_MESSAGES/django.mo
chmod -v 644 frontend/webpack/stats.json

chmod -v 755 new_static
# Find the files which doesn't have g+r,o+r (any of these)
find new_static/ -type f -type f ! -perm -g+r,o+r -exec chmod -v 644 '{}' +
# Find the directories which doesn't have g+rx,o+rx (any of these)
find new_static/  -type d ! -perm -g+rx,o+rx -exec chmod -v 755 '{}' +

# Create gzipped version of files for NGINX
find new_static/ -type f|xargs -n 1 -P 8 gzip --keep --best

# Ansible will deal with new_static/
# tar czf static.tar.gz new_static/ frontend/webpack/stats.json backend/switchershop/locale/de/LC_MESSAGES/django.mo
tar czf static.tar.gz new_static/ frontend/webpack/stats.json

mv -v new_static static
