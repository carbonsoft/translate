#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from python_tools.utils import run_bash_command
from python_tools.setup_logger import setupLogger
logger = setupLogger('translate')


def get_django_billing_words():
    logger.info(u'Генерируем фразы из админки биллинга')
    res = run_bash_command('gen_words /app/asr_billing/usr/local/www/sites')
    logger.info(res)


if __name__ == '__main__':
    get_django_billing_words()
