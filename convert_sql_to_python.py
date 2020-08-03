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


def convert_sql_file_to_list_with_insert_into_sql_lines(sql_file_path):
    pattern_sql_comment_slash = re.compile(r'^/\*?', re.IGNORECASE)
    pattern_sql_set = re.compile(r'^SET ', re.IGNORECASE)
    pattern_sql_connect = re.compile(r'^CONNECT ', re.IGNORECASE)
    pattern_sql_commit_work = re.compile(r'^COMMIT WORK;', re.IGNORECASE)
    pattern_sql_insert_into = re.compile(r'^INSERT INTO ', re.IGNORECASE)

    sql_insert_into_list = []
    with open(sql_file_path, 'r') as sql_file:
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
    return sql_insert_into_list


def convert_list_with_insert_into_sql_lines_to_json(sql_insert_into_list):
    pattern_insert_into = re.compile(r'INSERT INTO\s+(?P<table>.*)\s+\((?P<fields>.*)\)\s+VALUES\s+\((?P<values>.*)\);', re.IGNORECASE)
    pattern_split_by_comma = re.compile(',(?=(?:[^\']*\'[^\']*\')*[^\']*$)')

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
    return insert_into_data


def convert_json_to_python_variables(insert_into_json):
    python_variables_list = [
        '#!/usr/bin/python2.7',
        '# -*- coding: utf-8 -*-',
        'from django.utils.translation import ugettext as _'
    ]
    for table in insert_into_json:
        python_variables_list.append('# ' + table)
        for item in insert_into_json[table]:
            for key, value in item.iteritems():
                if not is_value_for_translate(value):
                    continue
                value = value.replace('\r', '\\r\\n')
                python_code = "variable = _(u'{val}')  # {comment}".format(val=value, comment=key)
                python_variables_list.append(python_code)
    return python_variables_list


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


def is_value_for_translate(value):
    if has_cyrillic(value):
        return True
    return False


def write_python_variables_to_code_file(python_file_path, python_variables_list):
    with open(python_file_path, 'w') as python_file:
        for python_code in python_variables_list:
            python_file.write(python_code + '\n')


def check_file_writable(file_path):
    if os.path.exists(file_path):
        if os.path.isfile(file_path):
            return os.access(file_path, os.W_OK)
        else:
            # path is a dir, so cannot write as a file
            return False
    parent_dir = os.path.dirname(file_path)
    if not parent_dir:
        parent_dir = '.'
    return os.access(parent_dir, os.W_OK)


def main(options):
    if not os.path.isfile(options.sql_dump):
        logger.error('{0} is not file'.format(options.sql_dump))
        return 2

    if not check_file_writable(options.python_file):
        logger.error('{0} is not file'.format(options.python_file))
        return 2

    sql_insert_into_list = convert_sql_file_to_list_with_insert_into_sql_lines(options.sql_dump)
    insert_into_data = convert_list_with_insert_into_sql_lines_to_json(sql_insert_into_list)
    python_variables = convert_json_to_python_variables(insert_into_data)
    write_python_variables_to_code_file(options.python_file, python_variables)
    logger.debug(json.dumps(python_variables, indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
    logger.info(json.dumps(len(python_variables), indent=2, sort_keys=True, ensure_ascii=False, encoding='utf8'))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert the SQL INSERT INTO to Python variables')
    parser.add_argument('--debug', help='Verbose output', action='store_true')
    parser.add_argument('--sql-dump', help='Path to SQL dump file with INSERT INTO', required=True)
    parser.add_argument('--python-file', help='Path to new Python file', default='data_system_translate.py')
    args = parser.parse_args()

    script_name = os.path.basename(sys.argv[0]).split('.py')[0]
    logger = setupLogger(script_name, use_stderr=True, level=logging.DEBUG if args.debug else logging.INFO)
    logger.debug('Exec {0} with params {1}'.format(sys.argv[0], args.__dict__))

    ret_code = main(args)
    sys.exit(ret_code)
