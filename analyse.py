# Author: Karan Bajaj (karanbajaj23@gmail.com)

import argparse
from parser.hdfc_parser import HDFCParser
from utils import parsing_utils


def create_args_parser():
    parser = argparse.ArgumentParser(description='Categorize expenses from bank statement')
    parser.add_argument('--file', required=True, type=str, help='Bank statement file')
    parser.add_argument('--config', type=str, default='./configs/hdfc.json', help='Bank expense config')
    parser.add_argument('--type', type=str, choices=['debit', 'credit', 'all'], default='all', help='Type of transactions')
    parser.add_argument('--all', required=False, action='store_true', help='Pass to print all expenses')
    parser.add_argument('--category', required=False, type=str, help='Category (optional)')
    parser.add_argument('--full_line', required=False, action='store_true', help='Show full transaction line')
    parser.add_argument('--credit', required=False, action='store_true', help='Show credit transactions')
    parser.add_argument('--month', required=False, type=int, help='Month (optional)')
    return parser

if __name__ == "__main__":
    args = create_args_parser().parse_args()
    parser = HDFCParser(args.config)
    ps_obj = parsing_utils.ParsedStatement(args.file)
    month_str = '0' + str(args.month) if args.month and args.month < 10 else str(args.month) if args.month else None
    filter_by = {'month': month_str, 'category': args.category, 'type': args.type}
    display_args = {'show_all': args.all, 'show_full_line': args.full_line}
    parser.parse_statement(ps_obj, filter_by, display_args)

