import re
import json
import argparse

from collections import OrderedDict, defaultdict

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
        self.date = parts2s[0]
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
            if len(amounts) != 2:
                raise Exception('ERROR: {}\n{}'.format(amounts, line))
            if len(dates) != 2:
                raise Exception('ERROR: {}\n{}'.format(dates, line))
            transaction_amt = amounts[0]
            date_len = len('01/01/20')
            if dates[0] == dates[1]:
                lpos = find_second_occurence(line, dates[1])+date_len-1
            else:
                lpos = line.find(dates[1])+date_len-1
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
            parts2s = filter(None, line.split('  '))
            tl = TransactionLine(line)
            found = False
            for t_substr in all_transaction_substrs:
                try:
                    if re.match(t_substr, tl.description):
                        transaction_groups[t_substr].append(TransactionLine(line))
                        found = True
                        break
                except:
                    print 'EXCEPTION with {}'.format(t_substr)
            if found and not display_args.get('show_all'):
                continue
            # print unclassified transactions
            print line.strip()

        format_str = '{0:9}  {1}'
        grand_total = 0
        header_str = '==================== categories ===================='
        print header_str
        for category_name, transaction_substrs in sorted(transaction_map.items()):
            total_transaction_amounts = 0
            for t_substr in transaction_substrs:
                total_transaction_amounts += sum([tl.amount for tl in transaction_groups.get(t_substr, [])])
            # only print non-zero amounts
            if total_transaction_amounts > 0:
                grand_total += total_transaction_amounts
                print format_str.format(total_transaction_amounts, category_name)
        print '.' * len(header_str)
        print format_str.format(grand_total, 'TOTAL')
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

        if show_credit:
            HDFCParser.parse_transactions(
                credit_lines,
                credit_map,
                detailed_category,
                display_args)
        else:
            HDFCParser.parse_transactions(
                debit_lines,
                debit_map,
                detailed_category,
                display_args)

def create_args_parser():
    parser = argparse.ArgumentParser(description='Categorize expenses from bank statement')
    parser.add_argument('--file', required=True, type=str, help='Bank statement file')
    parser.add_argument('--config', required=True, type=str, help='Bank expense config')
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
