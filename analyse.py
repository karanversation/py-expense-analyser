# Author: Karan Bajaj (karanbajaj23@gmail.com)

import argparse
from parser.hdfc_parser import HDFCParser


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

