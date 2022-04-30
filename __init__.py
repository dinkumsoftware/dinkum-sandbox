# dinkum/sudoku/__init__.py
# The suodku package import file
''' defines common definitions for all the sudoku modules.
These are typically constants.  There are All UPPER CASE
by dinkum convention.

Also defines a couple of Exceptions that can be raised
in various modules.
'''

# 2019-12-?? tc Initial
# 2019-12-03 tc Added ExcBadStrToConvert

import math

# Package wide constants
RCB_SIZE = 9 # num items in row/col/blk
NUM_CELLS = RCB_SIZE * RCB_SIZE
BLK_SIZE = int(math.sqrt(RCB_SIZE)) # Size of blocks e.g. 3x3 in 9x9 grid


# enums which label row/cols/blks
RCB_TYPE_ROW = 0
RCB_TYPE_COL = 1
RCB_TYPE_BLK = 2

ALL_RCB_TYPES = (RCB_TYPE_ROW, RCB_TYPE_COL, RCB_TYPE_BLK)
RCB_NAME  =     ("row",        "col",       "blk"        ) # indexed by rcb_type_X

# Exceptions we can toss
# The general approach is to raise an exception if the error is a result of user input.
# Otherwise, we assert things to perform sanity checks
class ExcUnsolvable(Exception) :
    def __init__(self) :
        self.message="Puzzle is NOT solvable"


class ExcBadPuzzleInput(Exception) :
    ''' Something wrong with puzzle given to be solved.
    Raiser should pass in error msg to contructor
    '''
    def __init__(self, message) :
        self.message=message

class ExcBadStrToConvert(Exception) :
    ''' Board.str_to_list_of_rows(str) encountered wrong
    number of digits in "str".
    '''
    def __init__(self) :
        self.message=  __doc__

    



