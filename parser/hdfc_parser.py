# Author: Karan Bajaj (karanbajaj23@gmail.com)

import re
import json
import decimal
from collections import OrderedDict, defaultdict
from utils import parsing_utils
from utils import format_utils
from utils.parsing_utils import inr, TransactionLine, ParsedStatement


class HDFCParser(object):

    def __init__(self, cfg_filepath):
        self.cfg_file = open(cfg_filepath, 'r')
        self.cat_cfg = json.load(self.cfg_file, object_pairs_hook=OrderedDict)

    @staticmethod
    def _trim_lines(lines):
        res_lines = []
        for line in lines:
            parts2s = filter(None, line.split('  '))
            res_line = '{0}  {1:45} {2}'.format(parts2s[0], parts2s[1], parts2s[-2])
            res_lines.append(res_line)
        return res_lines

    @staticmethod
    def parse_transactions(transaction_type, transaction_lines, transaction_map, detailed_category, display_args):
        format_utils.print_title_boundary(transaction_type, char='#')
        transaction_lines = HDFCParser._trim_lines(transaction_lines) if not display_args.get('show_full_line') else transaction_lines
        all_transaction_substrs = []
        for _, transaction_substrs in transaction_map.items():
            all_transaction_substrs.extend(transaction_substrs)

        transaction_groups = defaultdict(list)
        unclassified_lines = []
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
            unclassified_lines.append(line.strip())

        # print unclassified transactions
        if unclassified_lines:
            format_utils.print_title_boundary('UNCLASSIFIED', char='-')
            print '\n'.join(unclassified_lines)
            format_utils.print_boundary('-')

        format_str = '{0:>9}  {1}'
        grand_total = 0
        format_utils.print_title_boundary('categories', char='=')
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
        format_utils.print_boundary('.')
        print format_str.format(inr(grand_total), 'TOTAL')
        format_utils.print_boundary('=')

        if detailed_category and detailed_category in transaction_map:
            format_utils.print_title_boundary(detailed_category, char='=')
            grand_total = 0
            for t_substr in sorted(transaction_map.get(detailed_category, [])):
                total_transaction_amount = sum([tl.amount for tl in transaction_groups.get(t_substr, [])])
                # only print non-zero amounts
                if total_transaction_amount:
                    # print transaction lines
                    for tl in transaction_groups.get(t_substr):
                        print tl
                    format_utils.print_boundary('.')
                    print '{0:9} {1}'.format(total_transaction_amount, t_substr)
                    format_utils.print_boundary('=')
        format_utils.print_boundary('#')
        print ''

    def _print_monthly_summary(self, debit_lines, credit_lines):
        debit_trans_lines = [TransactionLine(dl) for dl in debit_lines]
        credit_trans_lines = [TransactionLine(cl) for cl in credit_lines]
        debit_monthly_grouped = parsing_utils.groupby(debit_trans_lines, lambda x: x.date.month, True)
        credit_monthly_grouped = parsing_utils.groupby(credit_trans_lines, lambda x: x.date.month, True)
        total_months = sorted(list(set(debit_monthly_grouped.keys()) | set(credit_monthly_grouped.keys())))
        format_utils.print_title_boundary('Monthly Summary', char='#')
        format_str = '{:<9}{:<14}{:<14}{:<14}'
        print format_str.format('Month', 'Debit(-)', 'Credit(+)', 'Savings')
        for month in total_months:
            total_debit = sum([tl.amount for tl in debit_monthly_grouped.get(month)]) if debit_monthly_grouped.get(month) else 0
            total_credit = sum([tl.amount for tl in credit_monthly_grouped.get(month)]) if credit_monthly_grouped.get(month) else 0
            print format_str.format(month, inr(total_debit), inr(total_credit), inr(total_credit-total_debit))
        format_utils.print_boundary('#')
        print ''

    def _separate_debit_credit(self, ps_obj):
        """
        Heuristic:
        Compare space b/w transaction amount, date and balance
        Amount closer to date -> debit
        Amount closer to balance -> credit
        """
        debit_lines = []
        credit_lines = []
        for line in ps_obj.stmt_lines:
            amounts = parsing_utils.get_amounts_from_line(line)
            dates = re.findall(r'\d\d/\d\d/\d\d', line)
            n_amounts = len(amounts)
            n_dates = len(dates)

            # skip line if amounts/dates <2
            if n_amounts < 2 or n_dates < 2:
                print 'ERROR: {} {}\n{}'.format(amounts, dates, line)
                continue

            date_len = len('01/01/20')
            right_date = dates[-1]
            if dates[0] == dates[1]:
                lpos = parsing_utils.find_second_occurence(line, right_date)+date_len-1
            else:
                lpos = line.find(right_date)+date_len-1
            """
            NOTE: There could be rows where n_amounts > 2
            Eg:
            05/04/21  CRV POS 512967******5730 HPCL 0.75% CASH  000000000000000   04/04/21                                  7.50        12345.67
            Here amounts = [0.75, 7.50, 12345.67]
            By default we pick amounts[-1] as rpos and amounts[-2] as amount_pos below
            """
            rpos = line.find(amounts[-1])
            amount_pos = line.find(amounts[-2])
            if (amount_pos-lpos) < (rpos-(amount_pos+len(amounts[0]))):
                debit_lines.append(line)
            else:
                credit_lines.append(line)
        return debit_lines, credit_lines

    def _filter_lines(self, ps_obj, month=None):
        re_str = r'\d+/\d+/\d+' if not month else r'\d+/{}/\d+'.format(month)
        # filter lines by regex (include check for month)
        ps_obj.stmt_lines = [l.strip() for l in ps_obj.stmt_lines if re.search(re_str, parsing_utils.get_line_part(l, 0))]
        # filter out lines that are part of ignore_transactions regex collection
        ps_obj.stmt_lines = [l for l in ps_obj.stmt_lines if not any(re.match(cat, parsing_utils.get_line_part(l, 1)) for cat in self.cat_cfg.get('ignore_transactions', []))]

    def _populate_category_maps(self):
        category_transaction_map = self.cat_cfg.get('category_transaction_map', {})
        debit_map = category_transaction_map.get('debit', {})
        credit_map = category_transaction_map.get('credit', {})

        # NOTE: common map transaction lines should not collide
        common_map = category_transaction_map.get('common', {})
        credit_map.update(common_map)
        debit_map.update(common_map)
        return credit_map, debit_map

    def parse_statement(self, ps_obj, filter_by, display_args):
        credit_map, debit_map = self._populate_category_maps()

        self._filter_lines(ps_obj, filter_by['month'])

        # TODO handle removal of reversed transactions

        # segregate transactions
        debit_lines, credit_lines = self._separate_debit_credit(ps_obj)

        # monthly total summary
        self._print_monthly_summary(debit_lines, credit_lines)

        show_credit = filter_by['type'] in ('credit', 'all')
        show_debit = filter_by['type'] in ('debit', 'all')
        if show_credit:
            HDFCParser.parse_transactions('Credit', credit_lines, credit_map, filter_by['category'], display_args)
        if show_debit:
            HDFCParser.parse_transactions('Debit', debit_lines, debit_map, filter_by['category'], display_args)

