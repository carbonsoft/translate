#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import re
import sys

from python_tools.setup_logger import setupLogger

logger = None


def main(options):
    if not os.path.isfile(options.sql_dump):
        logger.error('{0} is not file'.format(options.sql_dump))
        return 2

    with open(options.sql_dump, 'r') as sql_file:
        sql_raw = sql_file.read()
    sql_raw = sql_raw.replace('\n', '')

    insert_into_list = re.findall(r'INSERT INTO(.*?)VALUES(.*?);', sql_raw, re.IGNORECASE)

    del sql_raw
    del sql_file

    pattern_insert_into_head = re.compile(r'\s*(?P<table>.*)\s*\((?P<fields>.*)\)')
    pattern_insert_into_values = re.compile(r'\s*\(\s*(?P<values>.*)\s*\)\s*')

    res = {}

    for insert_into in insert_into_list:
        head = pattern_insert_into_head.search(insert_into[0]).groupdict()
        values = pattern_insert_into_values.search(insert_into[1]).groupdict()['values']
        table = head['table']
        fields = head['fields']
        content = {fields: values}
        if not res.get(table):
            res[table] = []
        res[table].append(content)

    del insert_into_list

    logger.info(json.dumps(res, indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert the SQL INSERT INTO to Python variables')
    parser.add_argument('--debug', help='Verbose output', action='store_true')
    parser.add_argument('--sql-dump', help='Path to SQL dump file with INSERT INTO', required=True)
    args = parser.parse_args()

    script_name = os.path.basename(sys.argv[0]).split('.py')[0]
    logger = setupLogger(script_name, use_stderr=True, level=logging.DEBUG if args.debug else logging.INFO)
    logger.debug('Exec {0} with params {1}'.format(sys.argv[0], args.__dict__))

    ret_code = main(args)
    sys.exit(ret_code)
