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

    pattern_sql_comment_slash = re.compile(r'^/\*?', re.IGNORECASE)
    pattern_sql_set = re.compile(r'^SET ', re.IGNORECASE)
    pattern_sql_connect = re.compile(r'^CONNECT ', re.IGNORECASE)
    pattern_sql_commit_work = re.compile(r'^COMMIT WORK;', re.IGNORECASE)
    pattern_sql_insert_into = re.compile(r'^INSERT INTO ', re.IGNORECASE)
    pattern_insert_into = re.compile(r'INSERT INTO\s+(?P<table>.*)\s+\((?P<fields>.*)\)\s+VALUES\s+\((?P<values>.*)\);', re.IGNORECASE)
    pattern_split_by_comma = re.compile(',(?=(?:[^\']*\'[^\']*\')*[^\']*$)')

    sql_insert_into_list = []
    with open(options.sql_dump, 'r') as sql_file:
        sql_insert_into_last_item = None
        for line in sql_file:
            line = line.strip()
            if line == '':
                continue
            if pattern_sql_comment_slash.match(line):
                continue
            if pattern_sql_set.match(line):
                continue
            if pattern_sql_connect.match(line):
                continue
            if pattern_sql_commit_work.match(line):
                continue
            if pattern_sql_insert_into.match(line):
                if sql_insert_into_last_item:
                    sql_insert_into_list.append(sql_insert_into_last_item)
                sql_insert_into_last_item = line
                continue
            sql_insert_into_last_item = sql_insert_into_last_item + '\r' + line
        sql_insert_into_list.append(sql_insert_into_last_item)
    del sql_file

    insert_into_data = {}
    for sql_insert_into in sql_insert_into_list:
        insert_into = pattern_insert_into.search(sql_insert_into).groupdict()
        table = insert_into['table'].upper()
        values = pattern_split_by_comma.split(insert_into['values'])
        fields = pattern_split_by_comma.split(insert_into['fields'])

        if len(fields) != len(values):
            logger.error('Not match fields {0} and values {1}'.format(len(fields), len(values)))
            logger.error(json.dumps(sql_insert_into, indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
            logger.error(json.dumps(fields, indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
            logger.error(json.dumps(values, indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
            continue

        content = {}
        for i, field in enumerate(fields):
            content[field.strip()] = values[i].strip().strip("'")

        if not insert_into_data.get(table):
            insert_into_data[table] = []
        insert_into_data[table].append(content)
    del sql_insert_into_list

    logger.info(json.dumps(insert_into_data, indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
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
