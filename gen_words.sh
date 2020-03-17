#!/bin/bash
. /app/base/usr/bin/activate

cd $1
python2.6 /app/base/usr/lib/python2.6/site-packages/django/bin/django-admin.py makemessages -l en -a \
        --no-wrap --no-location
echo  $1/locale/en/LC_MESSAGES/django.po
exit 0
