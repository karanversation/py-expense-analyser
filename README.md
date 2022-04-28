# pyStatementAnalyser
Python-based bank statement analyser\
Currently it only supports parsing HDFC bank statements downloaded in .txt format

## Usage

Complete Summary of the full statement -

```shell
$ python analyse.py --file <file_path>
```

Output -
```
################################ Monthly Summary ################################
Month    Debit(-)      Credit(+)     Savings
1        X,XX,XXX      X,XX,XXX      X,XX,XXX
         .....
12       X,XX,XXX     X,XX,XXX      (-) X,XX,XXX
#################################################################################

#################################### Credit #####################################
--------------------------------- UNCLASSIFIED ----------------------------------
02/01/21  XXXXXXXXXXXXXXXXXXXXXXX                        XX,XXX.XX
          .....
--------------------------------------------------------------------------------
================================== categories ===================================
XX,XX,XX  salary
          .....
................................................................................
XX,XX,XXX  TOTAL
   XX,XXX  UNCLASSIFIED
=================================================================================
#################################################################################

##################################### Debit #####################################
--------------------------------- UNCLASSIFIED ----------------------------------
01/02/21  XXXXXXXXXXXXXXXXXXXXXXX                        XX,XXX.XX
          .....
---------------------------------------------------------------------------------
================================== categories ===================================
XX,XX,XXX  other_bank_transfers
           .....
................................................................................
XX,XX,XXX  TOTAL
 X,XX,XXX  UNCLASSIFIED
=================================================================================
#################################################################################
```

### Filters

Filtered Summary for a month -

```shell
$ python analyse.py --file <file_path> --month <1-12>
```

Filtered Summary for a category -

```shell
$ python analyse.py --file <file_path> --category <category_name>
```

Output -
```
Complete Summary +
===================================== <category_name> ======================================
01/11/21  XXX-XXXX XXXXX XXXXXXX XXXXXXXXXXXXXXXXX       XXX.XX
          .....
.................................................................................
      XXX XXX-XXXX XXXXX
=================================================================================
#################################################################################
```

Filtered Summary for a transaction type (credit/debit/all) -

```shell
$ python analyse.py --file <file_path> --type <credit/debit/all>
```

Output -
```
################################ Monthly Summary ################################
Month    Debit(-)      Credit(+)     Savings
1        X,XX,XXX      X,XX,XXX      X,XX,XXX
         .....
12       X,XX,XXX     X,XX,XXX      (-) X,XX,XXX
#################################################################################

#################################### Credit #####################################
--------------------------------- UNCLASSIFIED ----------------------------------
02/01/21  XXXXXXXXXXXXXXXXXXXXXXX                        XX,XXX.XX
          .....
--------------------------------------------------------------------------------
================================== categories ===================================
XX,XX,XX  salary
          .....
................................................................................
XX,XX,XXX  TOTAL
   XX,XXX  UNCLASSIFIED
=================================================================================
#################################################################################
```

### Display options


Display all transactions along with the summary

```shell
$ python analyse.py --file <file_path> --all
```


Display the full line of transactions

```shell
$ python analyse.py --file <file_path> --all --full_line
```


## Example

```shell
$ python analyse.py --file 95380512_7845559435835.txt --month 05 --category online_shopping
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
