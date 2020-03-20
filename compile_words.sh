#!/bin/bash
# set -eu
# echo "$0 $@ [$$] START" >&2
. /app/base/usr/bin/activate
# echo Info: генерируем .po файлы для перевода
# echo Usage:  django_project_dir
# echo Example:  /app/asr_billing/usr/local/www/sites
BASE_DIR=/app/base/usr/local/www/base/
LOCALE_DIR=locale/en/LC_MESSAGES/
rm $BASE_DIR$LOCALE_DIR/*
cp ./*.po $BASE_DIR$LOCALE_DIR
cur_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $BASE_DIR

python2.6 /app/base/usr/lib/python2.6/site-packages/django/bin/django-admin.py compilemessages
cp $BASE_DIR/*.mo $cur_dir/
# echo "$0 $@ [$$] SUCCESS"
exit 0
