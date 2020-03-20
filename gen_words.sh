#!/bin/bash
# set -eu
# echo "$0 $@ [$$] START" >&2
. /app/base/usr/bin/activate
# echo Info: генерируем .po файлы для перевода
# echo Usage:  django_project_dir
# echo Example:  /app/asr_billing/usr/local/www/sites
dir=$1
is_django=${2:-1}
cd $dir
if [ "$is_django" = "1" ]; then
	python2.6 /app/base/usr/lib/python2.6/site-packages/django/bin/django-admin.py \
		makemessages -l en -a --no-wrap --no-location
	ls $dir/locale/en/LC_MESSAGES/*.po
else
	if [ -f $dir/translate.po ]; then
		pybabel extract $dir -o translate2.po
		pybabel update $dir -o translate.po -l en -i translate2.po
	else
		pybabel extract $dir -o translate.po
	fi
	ls $dir/translate.po
fi

# echo "$0 $@ [$$] SUCCESS"
exit 0
