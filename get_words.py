#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import filecmp
import logging
import os
import re
import shutil

import argparse


from python_tools.utils import run_bash_command
from python_tools.setup_logger import setupLogger
logger = setupLogger('translate', level=logging.INFO)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
BILLING_TR_PATH = CUR_DIR + '/admin_billing.po'
BASE_TR_PATH = CUR_DIR + '/base.po'
DAEMONS_TR_PATH = CUR_DIR + '/daemons.po'
BASE_DJANGO_PATH = CUR_DIR + '/django-appadmin/base/'
BILLING_DJANGO_PATH = CUR_DIR + '/djsite/sites/'
DAEMONS_PATH = CUR_DIR + '/daemons/'
DB_PATH = CUR_DIR + '/carbon_db/data_system.sql'
DJANGO_TR_FILE_PATH = 'locale/en/LC_MESSAGES/django.po'


def get_django_billing_words():
    logger.info(u'Добавляем фразы из базы данных в админку биллинга')
    res = run_bash_command(CUR_DIR + '/convert_sql_to_python.py --sql-dump {0}'.format(CUR_DIR + '/data_system.sql'))
    logger.info(res)
    if res[0] == 0:
        shutil.copy(CUR_DIR + '/data_system_translate.py', os.path.join(BILLING_DJANGO_PATH, 'admin'))

    logger.info(u'Генерируем фразы из админки биллинга')
    res = run_bash_command(CUR_DIR + '/gen_words.sh {0}'.format(BILLING_DJANGO_PATH))
    logger.info(res)
    if res[0]:
        raise Exception(u'Ошибка генерации фраз для перевода')
    shutil.copy(BILLING_DJANGO_PATH + DJANGO_TR_FILE_PATH, BILLING_TR_PATH)


def get_django_appadmin_words():
    logger.info(u'Генерируем фразы из платформы')
    res = run_bash_command(CUR_DIR + '/gen_words.sh {0}'.format(BASE_DJANGO_PATH))
    logger.info(res)
    if res[0]:
        raise Exception(u'Ошибка генерации фраз для перевода')
    shutil.copy(BASE_DJANGO_PATH + DJANGO_TR_FILE_PATH, BASE_TR_PATH)
    with open(BASE_TR_PATH, 'r') as f:
        with open(BASE_TR_PATH + '.tmp', 'w+') as f_tmp:
            for line in f.readlines():
                if line.startswith('#') or not line.strip():
                    continue
                if line.startswith('msgid'):
                    f_tmp.write("\n")
                f_tmp.write(line)
    shutil.move(BASE_TR_PATH + '.tmp', BASE_TR_PATH)


def get_daemons_words():
    logger.info(u'Генерируем фразы из демонов')
    copy_cmd = 'cp {CUR_DIR}/daemons.po {DST_DIR}/translate.po'.format(CUR_DIR=CUR_DIR,
                                                                       DST_DIR=DAEMONS_PATH)
    run_bash_command(copy_cmd)
    res = run_bash_command(CUR_DIR + '/gen_words.sh {0} 0'.format(DAEMONS_PATH))
    logger.info(res)
    if res[0]:
        raise Exception(u'Ошибка генерации фраз для перевода')
    shutil.copy(DAEMONS_PATH + 'translate.po', DAEMONS_TR_PATH)


def get_carbondb_data():
    logger.info(u'Проверяем появилось ли чтото новое в БД')
    carbondb_path = CUR_DIR + '/data_system.sql'
    if not os.path.isfile(carbondb_path) or not filecmp.cmp(carbondb_path, DB_PATH, shallow=False):
        logger.info(u'Изменилась база данных: необходимо обоновить перевод')
        shutil.copy(CUR_DIR + '/carbon_db/data_system.sql', carbondb_path)
    else:
        logger.info(u'База не поменялась')


def compile_translate():
    res = run_bash_command(CUR_DIR + '/compile_words.sh')
    if res[0]:
        logger.info(res)
        raise Exception(u'Не удалось скомпилировать перевод')
    logger.info(res)


def copy_no_overwrite(src_path, dst_path):
    if os.path.exists(src_path) and not os.path.exists(dst_path):
        shutil.copy(src_path, dst_path)


def clone_or_pull(repo_url, dir_name):
    cmd_clone = 'cd {0}; git clone {1}'.format(CUR_DIR, repo_url)
    cmd_pull = 'cd {0}/{1}; git reset --hard; git checkout integra; git pull'.format(CUR_DIR, dir_name)
    if not os.path.exists('{0}/{1}'.format(CUR_DIR, dir_name)):
        res = run_bash_command(cmd_clone)
        logger.info(res)
        if res[0]:
            raise Exception(u'Ошибка клонирования ' + repo_url)
    res = run_bash_command(cmd_pull)
    logger.info(res)
    if res[0]:
        raise Exception(u'Ошибка обновления ' + repo_url)


def _init():
    clone_or_pull('gitlab@git.carbonsoft.ru:crb5/daemons.git', 'daemons')
    clone_or_pull('gitlab@git.carbonsoft.ru:crb5/django-appadmin.git', 'django-appadmin')
    clone_or_pull('gitlab@git.carbonsoft.ru:crb5/djsite.git', 'djsite')
    clone_or_pull('gitlab@git.carbonsoft.ru:crb5/carbon_db.git', 'carbon_db')
    shutil.copy(DAEMONS_TR_PATH, os.path.join(DAEMONS_PATH, 'translate.po'))
    shutil.copy(BASE_TR_PATH, os.path.join(BASE_DJANGO_PATH, DJANGO_TR_FILE_PATH))
    shutil.copy(BILLING_TR_PATH, os.path.join(BILLING_DJANGO_PATH, DJANGO_TR_FILE_PATH))


def extract_variable_from_bash(variable, data):
    value = re.search(r'(.*?{0}.*?)\n'.format(variable), data).group(0).split('=')[1]
    value = value.replace("'", '').replace('\n', '')
    return value


def install():
    with open(os.path.join(CUR_DIR, 'translate.hook'), 'r') as hook_file:
        hook_data = hook_file.read()

    base_django_path = './' + extract_variable_from_bash('BASE_DJANGO_PATH', hook_data)
    billing_django_path = './' + extract_variable_from_bash('BILLING_DJANGO_PATH', hook_data)
    daemons_path = './' + extract_variable_from_bash('DAEMONS_PATH', hook_data)
    locale_path = extract_variable_from_bash('LOCALE_PATH', hook_data)

    daemons_tr_path = os.path.join('/app/asr_billing/', daemons_path, 'daemons.mo')
    billing_django_tr_path = os.path.join('/app/asr_billing/', billing_django_path, locale_path, 'django.mo')
    base_django_tr_path = os.path.join('/app/base/', base_django_path, locale_path, 'django.mo')

    shutil.copy(DAEMONS_TR_PATH.replace('.po', '.mo'), daemons_tr_path)
    shutil.copy(BILLING_TR_PATH.replace('.po', '.mo'), billing_django_tr_path)
    shutil.copy(BASE_TR_PATH.replace('.po', '.mo'), base_django_tr_path)

    logger.info(u'Перевод установлен')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Утилита получает файлы фраз для перевода посредством Django')
    parser.add_argument('--cmd', dest='cmd', default='get',
                        help='Получить файлы для перевода или скомпилировать текущие get/put')
    args = parser.parse_args()
    if args.cmd == 'get':
        _init()
        get_carbondb_data()
        get_django_billing_words()
        get_django_appadmin_words()
        get_daemons_words()
    elif args.cmd == 'put':
        compile_translate()
    elif args.cmd == 'init':
        _init()
    elif args.cmd == 'install':
        install()
