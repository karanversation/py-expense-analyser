# pyStatementAnalyser
Python-based bank statement analyser

## Usage

```shell
$ python hdfc.py --file <file_path> --month MM --category <category_name>
```
With optional args

```shell
$ python hdfc.py --file <file_path> --month MM --category <category_name> --all --category_all --full_line --credit
```

### Example

```shell
$ python hdfc.py --file 95380512_7845559435835.txt --month 05 --category online_shopping
```

Output -
```
==================== categories ====================
      XXX  amazon_pay
      XXX  bill_postpaid
    XXXXX  bill_society
      XXX  gas
    XXXXX  loan
     XXXX  medical
     XXXX  online_groceries
    XXXXX  online_shopping
     XXXX  other_card_payments
      XXX  paytm
    XXXXX  transfer_family
     XXXX  transfer_others
....................................................
   XXXXXX  TOTAL
====================================================

==================== online_shopping ====================
03/06/20  POS XXXXXXXXXXXXXXXX AMAZON                    XXXXX
03/06/20  POS XXXXXXXXXXXXXXXX AMAZON                    XXXXX
04/06/20  POS XXXXXXXXXXXXXXXX AMAZON                    XXXXX
06/06/20  POS XXXXXXXXXXXXXXXX AMAZON                    XXXXX
.........................................................
     XXXX POS \d{6}X{6}\d{4} AMAZON
=========================================================
19/06/20  POS XXXXXXXXXXXXXXXX MYNTRA DESIGNS P          XXXXX
.........................................................
     XXXX POS \d{6}X{6}\d{4} MYNTRA DESIGNS P
=========================================================
06/06/20  POS XXXXXXXXXXXXXXXX PAYU-FLIPKART PA          XXXXX
13/06/20  POS XXXXXXXXXXXXXXXX PAYU-FLIPKART PA          XXXXX
13/06/20  POS XXXXXXXXXXXXXXXX PAYU-FLIPKART PA          XXXXX
20/06/20  POS XXXXXXXXXXXXXXXX PAYU-FLIPKART PA          XXXXX
.........................................................
     XXXX POS \d{6}X{6}\d{4} PAYU-FLIPKART PA
=========================================================
```
