#!/bin/bash
# echo "$0 $@ [$$] START" >&2
. /app/base/usr/bin/activate
echo Info: генерируем .po файлы для перевода
echo Usage:  django_project_dir
echo Example:  /app/asr_billing/usr/local/www/sites

cd $1
python2.6 /app/base/usr/lib/python2.6/site-packages/django/bin/django-admin.py \
	makemessages -l en -a --no-wrap --no-location
echo  $1/locale/en/LC_MESSAGES/django.po
# echo "$0 $@ [$$] SUCCESS"
exit 0
