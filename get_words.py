#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import logging
import os
import shutil

import argparse


from python_tools.utils import run_bash_command
from python_tools.setup_logger import setupLogger
logger = setupLogger('translate', level=logging.INFO)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
BILLING_TR_PATH = CUR_DIR + '/admin_billing.po'
BASE_TR_PATH = CUR_DIR + '/base.po'
DAEMONS_TR_PATH = CUR_DIR + '/daemons.po'
BASE_DJANGO_PATH = '/app/base/usr/local/www/base/'
BILLING_DJANGO_PATH = '/app/asr_billing/usr/local/www/sites/'
DAEMONS_PATH = '/app/asr_billing/usr/lib/python2.7/site-packages/daemons/'
DJANGO_TR_FILE_PATH = 'locale/en/LC_MESSAGES/django.po'


def get_django_billing_words():
    logger.info(u'Генерируем фразы из админки биллинга')
    res = run_bash_command(CUR_DIR + '/gen_words.sh {0}'.format(BILLING_DJANGO_PATH))
    logger.info(res)
    if res[0]:
        raise Exception(u'Ошибка генерации фраз для перевода')
    shutil.copy(BILLING_DJANGO_PATH + DJANGO_TR_FILE_PATH, BILLING_TR_PATH)
    # TODO пока закомментируем
    # _get_daemons_words()
    # # Обьединим переводы
    # couple = False
    # with open(BILLING_TR_PATH, 'r') as billing_tr_file:
    #     billing_tr = billing_tr_file.readlines()
    #     with open(DAEMONS_TR_PATH, 'r') as daemons_tr_file:
    #         for line in daemons_tr_file.readlines():
    #             if not line.strip() or line.startswith('#'):
    #                 continue
    #             if couple and line.startswith('msgstr'):
    #                 couple = False
    #                 continue
    #             if line in billing_tr and line.startswith('msgid'):
    #                 couple = True
    #                 continue
    #             billing_tr.append(line)
    #     os.remove(DAEMONS_TR_PATH)
    # # Запишем новый перевод
    # with open(BILLING_TR_PATH, 'w') as billing_tr_file:
    #     for line in billing_tr:
    #         if line.startswith('#') or not line.strip():
    #             continue
    #         if line.startswith('msgid'):
    #             billing_tr_file.write("\n")
    #         billing_tr_file.write(line)


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


def compile_translate():
    res = run_bash_command(CUR_DIR + '/compile_words.sh')
    logger.info(res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Утилита получает файлы фраз для перевода посредством Django')
    parser.add_argument('--cmd', dest='cmd', default='get',
                        help='Получить файлы для перевода или скомпилировать текущие get/put')
    args = parser.parse_args()
    if args.cmd == 'get':
        get_django_billing_words()
        get_django_appadmin_words()
        get_daemons_words()
    elif args.cmd == 'put':
        compile_translate()
