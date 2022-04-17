# Author: Karan Bajaj (karanbajaj23@gmail.com)

import re
from datetime import datetime
from collections import OrderedDict


def inr(value):
    value = str(int(value))
    neg = False
    if value.startswith('-'):
        neg = True
        value = value[1:]
    prefix = '(-) ' if neg else ''
    if len(value) <= 3:
        return '{}{}'.format(prefix, value)
    value_2 = str(value[:-3][::-1])
    res = ','.join([value_2[i:i+2] for i in range(0, len(value_2), 2)])
    return '{}{},{}'.format(prefix, res[::-1], value[-3:])

def groupby(iterable, key, to_dict=False):
    ret = OrderedDict()
    for i in iterable:
        k = key(i)
        if k not in ret:
            ret[k] = []
        ret[k].append(i)
    return ret if to_dict else list(ret.items())

def _str_amount_to_int(amount):
    return int(amount.replace(',', '')[:-3])

def split_line(line):
    return filter(None, line.split('  '))

def get_line_part(line, index):
    return split_line(line)[index]

def find_second_occurence(line, sub):
    return line.find(sub, line.find(sub)+1)

def get_amounts_from_line(line):
    return re.findall(r'\d*,?\d+\,?\d{0,3}\.\d{2}', line)


class TransactionLine(object):

    def __init__(self, line):
        self.line = line
        parts2s = split_line(line)
        self.date = datetime.strptime(parts2s[0], '%d/%m/%y')
        self.description = parts2s[1]
        self.amount = _str_amount_to_int(get_amounts_from_line(line)[0])

    def __repr__(self):
        return self.line


class ParsedStatement(object):

    def __init__(self, stmt_filepath):
        self.stmt_filepath = stmt_filepath
        self.stmt_file = open(self.stmt_filepath, 'r')
        self.stmt_lines = self.stmt_file.readlines()

    def __repr__(self):
        return 'ParsedStatement({})'.format(self.stmt_filepath)
