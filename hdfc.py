# Author: Karan Bajaj (karanbajaj23@gmail.com)

import re
import json
import decimal
import argparse
from datetime import datetime
from collections import OrderedDict, defaultdict


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

def str_amount_to_int(amount):
    return int(amount.replace(',', '')[:-3])

def get_line_part(line, index):
    return filter(None, line.split('  '))[index]

def find_second_occurence(line, sub):
    return line.find(sub, line.find(sub)+1)

def get_amounts_from_line(line):
    return re.findall(r'\d*,?\d+\,?\d{0,3}\.\d{2}', line)

class TransactionLine(object):

    def __init__(self, line):
        parts2s = filter(None, line.split('  '))
        self.line = line
        self.date = datetime.strptime(parts2s[0], '%d/%m/%y')
        self.description = parts2s[1]
        self.amount = str_amount_to_int(get_amounts_from_line(line)[0])

    def __repr__(self):
        return self.line


class HDFCParser(object):

    def __init__(self, stmt_filepath, cfg_filepath):
        self.stmt_file = open(stmt_filepath, 'r')
        self.cfg_file = open(cfg_filepath, 'r')
        self.stmt_lines = self.stmt_file.readlines()
        self.cat_cfg = json.load(self.cfg_file, object_pairs_hook=OrderedDict)

    def _filter_valid_transactions(self, month=None):
        re_str = r'\d+/\d+/\d+' if not month else r'\d+/{}/\d+'.format(month)
        self.stmt_lines = [l.strip() for l in self.stmt_lines if re.search(re_str, get_line_part(l, 0))]

    def _remove_ignore_transactions(self):
        self.stmt_lines = [l for l in self.stmt_lines if not any(re.match(cat, get_line_part(l, 1)) for cat in self.cat_cfg.get('ignore_transactions', []))]

    def _separate_debit_credit(self):
        """
        Heuristic:
        Compare space b/w transaction amount, date and balance
        Amount closer to date -> debit
        Amount closer to balance -> credit
        """
        debit_lines = []
        credit_lines = []
        for line in self.stmt_lines:
            amounts = get_amounts_from_line(line)
            dates = re.findall(r'\d\d/\d\d/\d\d', line)
            n_amounts = len(amounts)
            n_dates = len(dates)

            # skip line if amounts/dates <2
            if n_amounts < 2 or n_dates < 2:
                print 'ERROR: {} {}\n{}'.format(amounts, dates, line)
                continue
            # show warning if >2
            if n_amounts > 2 or n_dates > 2:
                print 'WARNING (Heuristic expects 2 each of amounts and dates):\n{} {}\n{}'.format(amounts, dates, line)

            date_len = len('01/01/20')
            right_date = dates[-1]
            if dates[0] == dates[1]:
                lpos = find_second_occurence(line, right_date)+date_len-1
            else:
                lpos = line.find(right_date)+date_len-1
            rpos = line.find(amounts[1])
            amount_pos = line.find(amounts[0])
            if (amount_pos-lpos) < (rpos-(amount_pos+len(amounts[0]))):
                debit_lines.append(line)
            else:
                credit_lines.append(line)
        return debit_lines, credit_lines

    @staticmethod
    def _trim_lines(lines):
        res_lines = []
        for line in lines:
            parts2s = filter(None, line.split('  '))
            res_line = '{0}  {1:45} {2}'.format(parts2s[0], parts2s[1], parts2s[-2])
            res_lines.append(res_line)
        return res_lines

    @staticmethod
    def parse_transactions(transaction_lines, transaction_map, detailed_category, display_args):
        transaction_lines = HDFCParser._trim_lines(transaction_lines) if not display_args.get('show_full_line') else transaction_lines
        all_transaction_substrs = []
        for _, transaction_substrs in transaction_map.items():
            all_transaction_substrs.extend(transaction_substrs)

        transaction_groups = defaultdict(list)
        for line in transaction_lines:
            tl = TransactionLine(line)
            found = False
            for t_substr in all_transaction_substrs:
                try:
                    if re.match(t_substr, tl.description):
                        transaction_groups[t_substr].append(tl)
                        found = True
                        break
                except:
                    print 'EXCEPTION with {}'.format(t_substr)
            if found and not display_args.get('show_all'):
                continue
            # print unclassified transactions
            print line.strip()

        format_str = '{0:>9}  {1}'
        grand_total = 0
        header_str = '==================== categories ===================='
        print header_str
        category_amounts = []
        for category_name, transaction_substrs in sorted(transaction_map.items()):
            total_transaction_amounts = 0
            for t_substr in transaction_substrs:
                total_transaction_amounts += sum([tl.amount for tl in transaction_groups.get(t_substr, [])])
            # only print non-zero amounts
            if total_transaction_amounts > 0:
                grand_total += total_transaction_amounts
                category_amounts.append((category_name, total_transaction_amounts))
        category_amounts.sort(key=lambda x:x[1], reverse=True)
        for ca in category_amounts:
            print format_str.format(inr(ca[1]), ca[0])
        print '.' * len(header_str)
        print format_str.format(inr(grand_total), 'TOTAL')
        print '=' * len(header_str) + '\n'

        if detailed_category and detailed_category in transaction_map:
            header_str = '==================== {} ===================='.format(detailed_category)
            print header_str
            grand_total = 0
            for t_substr in sorted(transaction_map.get(detailed_category, [])):
                total_transaction_amount = sum([tl.amount for tl in transaction_groups.get(t_substr, [])])
                # only print non-zero amounts
                if total_transaction_amount:
                    # print transaction lines
                    for tl in transaction_groups.get(t_substr):
                        print tl
                    print '.' * len(header_str)
                    print '{0:9} {1}'.format(total_transaction_amount, t_substr)
                    print '=' * len(header_str)

    def print_monthly_summary(self, debit_lines, credit_lines):
        debit_trans_lines = [TransactionLine(dl) for dl in debit_lines]
        credit_trans_lines = [TransactionLine(cl) for cl in credit_lines]
        debit_monthly_grouped = groupby(debit_trans_lines, lambda x: x.date.month, True)
        credit_monthly_grouped = groupby(credit_trans_lines, lambda x: x.date.month, True)
        total_months = sorted(list(set(debit_monthly_grouped.keys()) | set(credit_monthly_grouped.keys())))
        print '==================== Monthly Summary ===================='
        format_str = '{:<9}{:<14}{:<14}{:<14}'
        print format_str.format('Month', 'Debit', 'Credit', 'Diff')
        for month in total_months:
            total_debit = sum([tl.amount for tl in debit_monthly_grouped.get(month)]) if debit_monthly_grouped.get(month) else 0
            total_credit = sum([tl.amount for tl in credit_monthly_grouped.get(month)]) if credit_monthly_grouped.get(month) else 0
            print format_str.format(month, inr(total_debit), inr(total_credit), inr(total_credit-total_debit))
        print '========================================================='

    def parse_txt(self, month, detailed_category, show_credit, display_args):
        category_transaction_map = self.cat_cfg.get('category_transaction_map', {})
        debit_map = category_transaction_map.get('debit', {})
        credit_map = category_transaction_map.get('credit', {})

        # NOTE: common map transaction lines should not collide
        common_map = category_transaction_map.get('common', {})
        credit_map.update(common_map)
        debit_map.update(common_map)

        # filter step
        self._filter_valid_transactions(month)
        self._remove_ignore_transactions()

        # TODO handle removal of reversed transactions

        # segregate transactions
        debit_lines, credit_lines = self._separate_debit_credit()

        # monthly total summary
        self.print_monthly_summary(debit_lines, credit_lines)

        if show_credit:
            HDFCParser.parse_transactions(credit_lines, credit_map, detailed_category, display_args)
        else:
            HDFCParser.parse_transactions(debit_lines, debit_map, detailed_category, display_args)

def create_args_parser():
    parser = argparse.ArgumentParser(description='Categorize expenses from bank statement')
    parser.add_argument('--file', required=True, type=str, help='Bank statement file')
    parser.add_argument('--config', type=str, default='./configs/hdfc.json', help='Bank expense config')
    parser.add_argument('--month', required=False, type=str, help='Month (optional)')
    parser.add_argument('--all', required=False, action='store_true', help='Pass to print all expenses')
    parser.add_argument('--category', required=False, type=str, help='Category (optional)')
    parser.add_argument('--category_all', required=False, type=str, help='Show all transaction lines for category (optional)')
    parser.add_argument('--full_line', required=False, action='store_true', help='Show full transaction line')
    parser.add_argument('--credit', required=False, action='store_true', help='Show credit transactions')
    return parser

if __name__ == "__main__":
    args = create_args_parser().parse_args()
    parser = HDFCParser(args.file, args.config)
    display_args = {
        'show_all': args.all,
        'show_category_all': args.category_all,
        'show_full_line': args.full_line
    }
    parser.parse_txt(args.month, args.category, args.credit, display_args)
