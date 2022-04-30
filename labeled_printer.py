#!/usr/bin/env python3
# dinkum/sudoku/labeled_printer.py
''' Has a function, print_labeled_board, which prints a human-readable
board with all the cell numbers, row numbers, column numbers, and
block numbers labeled.

Cell values are shown in middle of cell and number of possible_values for
unsolved cells are shown in lower left of the cell.

It's a rather busy printout, probably only of interest to developers.

Example empty board:
(with want_cell_nums==True and want_num_possibles==True)

     0     1     2      3     4     5      6     7     8     
 /---------------------------------------------------------\ 
 |0------------------1------------------2------------------| 
 |0     1     2     |3     4     5     |6     7     8     || 
0||     |     |     ||     |     |     ||     |     |     ||0
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |9     10    11    |12    13    14    |15    16    17    || 
1||     |     |     ||     |     |     ||     |     |     ||1
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |18    19    20    |21    22    23    |24    25    26    || 
2||     |     |     ||     |     |     ||     |     |     ||2
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |3------------------4------------------5------------------| 
 |27    28    29    |30    31    32    |33    34    35    || 
3||     |     |     ||     |     |     ||     |     |     ||3
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |36    37    38    |39    40    41    |42    43    44    || 
4||     |     |     ||     |     |     ||     |     |     ||4
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |45    46    47    |48    49    50    |51    52    53    || 
5||     |     |     ||     |     |     ||     |     |     ||5
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |6------------------7------------------8------------------| 
 |54    55    56    |57    58    59    |60    61    62    || 
6||     |     |     ||     |     |     ||     |     |     ||6
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |63    64    65    |66    67    68    |69    70    71    || 
7||     |     |     ||     |     |     ||     |     |     ||7
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 |---------------------------------------------------------| 
 |72    73    74    |75    76    77    |78    79    80    || 
8||     |     |     ||     |     |     ||     |     |     ||8
 ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || 
 \---------------------------------------------------------/ 
     0     1     2      3     4     5      6     7     8           
'''

# 2019-11-23 tc Refactored from dinkum_print_sukoku_worksheet.py
#                  worksheet() ==> print_labeled_board()
#               added cell values             
# 2019-11-25 tc print_labeled_board() ==> labeled_board_lines()
#               Made print_labeled_board() actually print the lines
#               Added cell values
#               Moved block label location
# 2019-11-26 tc Fixed import problem
# 2019-12-01 tc minor todo knockoff.  get row# from rgb rather than cell
# 2019-12-03 tc Made cell# and num_possible printouts optional

#--------------------------------------------------------------
from dinkum.sudoku.board    import *
from dinkum.utils.str_utils import *

# What we make lines with
horz_line_char = '-'
vert_line_char = '|'

# size of printed cell
# includes rightmost | and topmost -
# does NOT include leftmost | and bottom -
# does NOT include any block separators
cell_width   = 6
cell_height  = 4

# Width of whole printed board
left_offset_to_first_cell = 2           # Accounts for row label and one |
right_pad_after_last_cell = 3           # || + row_label
width_of_internal_block_separators = 2  # Two internal |'s

output_width = left_offset_to_first_cell + cell_width * RCB_SIZE +     \
               width_of_internal_block_separators + right_pad_after_last_cell

# Height of whole printed board
top_offset_to_first_cell = 2 # column label + '-'
bot_pad_after_last_cell  = 2 # bottom cell '-' + '-' + column_label

def print_labeled_board(board=None, want_cell_nums=True, want_num_possibles=False) :
    ''' prints the output of labeled_board() resulting
    in a human-readable board showing cell values with
    everything (cell#,row#, col#,blk#) labeled.

    If board isn't supplied, produces output for an empty board.
    want_cell_nums controls whether cell number labels are output
    want_num_possibles controls whether num_possibles for each cell
    are output.

    '''
    for l in labeled_board(board, want_cell_nums, want_num_possibles) :
        print (l) 


def labeled_board(board=None, want_cell_nums=True, want_num_possibles=False) :
    ''' outputs board with all column, row, block, and
    cell's labeled along with the cell values in human
    readable format.

    Returns a [] of lines (NOT terminated by new line) that
    make up the board

    If board is not supplied, produces output for an empty board
    '''
    if not board :
        board = Board(None, None, "created by labeled_board()")

    ws = [] # What we return

    #    0  1  2 ...
    # /--------------------------------\  #
    ws += top_or_bottom_lines(is_top=True)

    # Stuff in the middle, e.g.
    # 1|  9 10 11 | 12 13 14 | 15 16 17 |1
    for row in board.rows :
        ws += row_line(row, want_cell_nums, want_num_possibles)

    # \ --------------------------------/ #
    #    0  1  2 ...
    ws += top_or_bottom_lines(is_top=False)
        
    return ws


def top_or_bottom_lines(is_top) :
    ''' returns [] of [column label line, horz separator line. e.g.
    is_top controls whether top or bottom lines.  Example of a top line
        0     1     2      3     4     5      6     7     8     
    /---------------------------------------------------------\ 
    '''

    if is_top :
        # column label and separator line
        ret_list  = col_label_lines()               # 0 1 2 ...
        ret_list += horz_separator_lines('/', '\\') # /----------\
        assert len(ret_list) == top_offset_to_first_cell
        return ret_list

    else :
        # bottom
        ret_list =  horz_separator_lines('\\', '/')                       # \---------------/ 
        ret_list += col_label_lines()                                     #     0     1   2 ...

        assert len(ret_list) == bot_pad_after_last_cell
        return ret_list

    assert False, "Impossible Place"

def row_line(row, want_cell_nums, want_num_possibles) :
    ''' returns [] of lines that make up a row of cells
    lines are NOT \n terminated.

    want_cell_nums controls whether the cell number is labeled.
    want_num_possibles controls whether num_possibles is output

    The top line, left, and right cell outlines are include
    in returned lines.  A horizontal block separator may
    be included in the output.

    The bottom cell lines are NOT in the returned lines.

    The cell number is written in the upper left corner of
    the cell area

    Example return:
     |---------------------------------------------------------| 
     |9     10    11    |12    13    14    |15    16    17    || 
    1||     |     |     ||     |     |     ||     |     |     ||1
     ||     |     |     ||     |     |     ||     |     |     || 

    '''

    # Which row we are working on
    row_num = row.rcb_num

    # What we return.  Gets filled in below                     
    ret_lines= [None] * cell_height

    # A cell consists of the left and top border, spaces inside,
    # but NOT the bottom and right border

    # Start with a separator line. This is top line of all cells in
    # the row.  block number labels will be inserted into this line
    # above and below the middle cell in the block. Example:
    #  |---------------------------------------------------------| 
    ret_lines = horz_separator_lines()

    # Each individual row is made of multiple output lines.
    # Iterate over them
    first_line_of_cell_content = 1 # skips horz_separator_lines
    for line_num_in_row in range(first_line_of_cell_content, cell_height) :
        # example:
        #    1||     |     |     ||     |     |     ||     |     |     ||1
        line = '' # start with an empty line and append to it
                  # moving left to right

        # Time to place row label on outside ?
        line += str(row_num) if line_num_in_row == cell_height//2 else ' '

        line += vert_line_char 

        # We iterate over a row of Cells in a Board so
        # we don't have to do the arithmetic for cell#, block#, etc
        # Output the left edge and appropriate number of spaces
        for cell in row :
            # Need to label the block in prior line?
            # example: 
            #  |3------------------4------------------5------------------| 
            #  |27    28    29    |30    31    32    |33    34    35    || 
            if line_num_in_row == first_line_of_cell_content and cell.blk_idx == 0 :
                # yes, it's first cell in block
                ret_lines[0] = replace_substr_at(ret_lines[0], str(cell.blk_num),
                                                 block_label_offset_in_line(cell))

            # cell's left edge
            line += vert_line_char

            # spaces of the cell
            cell_content = ' ' * (cell_width-1) # The -1 is for vert_line_char we just printed

            # Time to write the cell's value (if there is one)?
            # example:
            #   |72    73    74    |75    76    77    |78    79    80    ||
            #  8||  1  |     |     ||     |     |  2  ||  5  |  3  |  4  ||8
            #   ||     |6    |3    ||2    |4    |     ||     |     |     ||
            #   \---------------------------------------------------------/
            # number in middle is cell's value
            # number in lower left is num_possibles

            # Note: This is so complicated because I originally indended
            #       to write the value multiple times in a square.  I thought
            #       this looked better, but I left the more general code in.
            value_label_vert_offset_in_cell = 2
            value_label_vert_num = 1
            value_label_horz_offset_in_cell = 2
            value_label_horz_num = 1
            if cell.value != Cell.unsolved_cell_value :
                # There is value to print, on the right line?
                if (value_label_vert_offset_in_cell <=
                    line_num_in_row <
                    (value_label_vert_offset_in_cell + value_label_vert_num)) :
                    # Yes, replace the chars
                    cell_content = replace_substr_at(cell_content, str(cell.value) * value_label_horz_num,
                                                     value_label_horz_offset_in_cell)
            else :
                # cell is unsolved, maybe a number of possible values
                #    in lower left corner on last line
                num_possibles_label_horz_offset_in_cell = 0
                if want_num_possibles :
                    if line_num_in_row == (cell_height-1) :
                        cell_content=replace_substr_at(cell_content, str(len(cell.possible_values)),
                                                       num_possibles_label_horz_offset_in_cell)

            line += cell_content # Tack it on

            # We have entirely written the output associated with this cell

            # on top line only, maybe label the cell number
            # We overwrite the left vertical separater and the
            # first char in cell_content
            if want_cell_nums and line_num_in_row == first_line_of_cell_content:
                cell_label = "%d" % cell.cell_num
                line = replace_substr_at(line, cell_label, -cell_width)

            # Time to place an internal (not on edges) vertical block separator ?
            if is_cell_rightmost_in_block_and_internal(cell.col_num) :
                line += vert_line_char

        # right border of last cell in the row (the one we just output)
        line += vert_line_char 

        # Outside right line
        line += vert_line_char 

        # Time to place row label on outside ?
        line += str(row_num) if line_num_in_row == cell_height//2 else ' '

        # All done composing line
        assert len(line) == output_width, "is: %d, should be:%d" %(len(line), output_width)

        # Set our result in the [] we return
        ret_lines.append(line)

    assert len(ret_lines) == cell_height

    # If this is the bottom row of an internal block, we need
    # to separate it by adding another line of ----------'s
    if is_cell_bottom_most_in_block_and_internal(row_num) :
        ret_lines += horz_separator_lines()

    return ret_lines

def horz_separator_lines(first_char=vert_line_char, last_char=vert_line_char) :
    ''' Returns [] of lines making up top or bottom
    lines, e.g.
           0     1     2      3     4     5      6     7     8     
       /---------------------------------------------------------\ 

    The first and last chars of each line are set to
    first_char and last_char
    lines are NOT new line terminated.
    '''

    # -----------
    # Start with full line of lines
    # and overwrite what we need to
    sep_line = horz_line_char * output_width

    # Overwrite first and last chars with spaces
    # to account for row label's

    sep_line = replace_substr_at(sep_line, ' ',  0)
    sep_line = replace_substr_at(sep_line, ' ' , -1)

    # overwrite first and last chars that were passed in                    
    sep_line = replace_substr_at(sep_line, first_char,  1)
    sep_line = replace_substr_at(sep_line, last_char , -2)

    # All done
    return [sep_line]

def col_label_lines() :
    ''' returns [] of lines that label the columns.
    Each line is NOT \n terminated.
    '''
    
    # Start with stuff on left before first Cell
    # "   "
    col_label_line = left_pad()

    # Do the stuff above a row of cells
    # We don't care which row
    row = Board().rows[0]

    for cell in row :
        # A cell_width blank string
        cell_line = ' ' * cell_width

        # Write column label in the middle
        cell_line = replace_substr_at(cell_line, str(cell.col_num),
                                      len(cell_line)//2 )

        # We have to account for vertical block separators
        # to keep the center alignment of column numbers
        if is_cell_rightmost_in_block_and_internal(cell.col_num) :
            cell_line += ' '

        # Tack it on
        col_label_line += cell_line
    
    # Fill out the rest of the line
    # "   "
    col_label_line += right_pad()

    # Give them back list of our one generated line
    return [col_label_line]
    
def is_cell_rightmost_in_block_and_internal(col_num) :
    ''' Returns true if cell in col_num needs a block
    separator to it's right AND it isn't the last cell
    on the line.  Hence the internal word
    '''
    return col_num==2  or col_num==5

def is_cell_bottom_most_in_block_and_internal(row_num) :
    ''' Returns True if the row at row_num is the
    bottommost row of the block AND and not on the
    bottom row of the board, hence the use of internal.
    '''
    return row_num==2 or row_num==5

def is_cell_above_in_middle_of_block(cell) :
    ''' returns TRUE if cell is the center cell
    of it's block
    '''
    return cell.row_num in [1,4,7] and cell.col_num in [1,4,7]


def is_cell_in_middle_of_block(cell) :
    ''' returns TRUE if cell is the center cell
    in the bottom row of it's block.
    '''
    return cell.row_num in [2,5,8] and cell.col_num in [1,4,7]


def block_label_offset_in_line(cell) :
    ''' Returns the offset in a full output line where
    the block label of cell should be placed.
    :example
      |0------------------1------------------2------------------| 
    '''

    # The label is in the upper right corner of the first
    # cell (upper left) in the block
    block_label_offset = top_offset_to_first_cell # offset for cell 0

    # Move it over as required
    blk_in_line = cell.blk_num %  BLK_SIZE # 0,1,or 2
    num_vert_separator_lines = blk_in_line  # How many internal |s there are
    block_label_offset +=  blk_in_line * BLK_SIZE * cell_width + num_vert_separator_lines

    return block_label_offset

def left_pad() :
    ''' Returns a string that makes up the left edge of the output board.
    '''
    ret_str = '  '
    assert len(ret_str) == left_offset_to_first_cell
    return ret_str


def right_pad() :
    ''' Returns a string that makes up the right edge of the output board.
        It's all spaces.
    '''
    ret_str = '   '
    assert len(ret_str) == right_pad_after_last_cell

    return ret_str



# Test code
import unittest

class Test_labeled_printer(unittest.TestCase):

    # How an empty board is printed with various combinations
    # of Used in multiple tests
    expected_empty_output_cell_and_num_possible =\
        [\
         "     0     1     2      3     4     5      6     7     8     ",
         " /---------------------------------------------------------\ ",
         " |0------------------1------------------2------------------| ",
         " |0     1     2     |3     4     5     |6     7     8     || ",
         "0||     |     |     ||     |     |     ||     |     |     ||0",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |9     10    11    |12    13    14    |15    16    17    || ",
         "1||     |     |     ||     |     |     ||     |     |     ||1",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |18    19    20    |21    22    23    |24    25    26    || ",
         "2||     |     |     ||     |     |     ||     |     |     ||2",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |3------------------4------------------5------------------| ",
         " |27    28    29    |30    31    32    |33    34    35    || ",
         "3||     |     |     ||     |     |     ||     |     |     ||3",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |36    37    38    |39    40    41    |42    43    44    || ",
         "4||     |     |     ||     |     |     ||     |     |     ||4",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |45    46    47    |48    49    50    |51    52    53    || ",
         "5||     |     |     ||     |     |     ||     |     |     ||5",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |6------------------7------------------8------------------| ",
         " |54    55    56    |57    58    59    |60    61    62    || ",
         "6||     |     |     ||     |     |     ||     |     |     ||6",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |63    64    65    |66    67    68    |69    70    71    || ",
         "7||     |     |     ||     |     |     ||     |     |     ||7",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " |---------------------------------------------------------| ",
         " |72    73    74    |75    76    77    |78    79    80    || ",
         "8||     |     |     ||     |     |     ||     |     |     ||8",
         " ||9    |9    |9    ||9    |9    |9    ||9    |9    |9    || ",
         " \---------------------------------------------------------/ ",
         "     0     1     2      3     4     5      6     7     8     ",
        ]

    expected_empty_output =\
        [\
         "     0     1     2      3     4     5      6     7     8     ",
         " /---------------------------------------------------------\ ",
         " |0------------------1------------------2------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "0||     |     |     ||     |     |     ||     |     |     ||0",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "1||     |     |     ||     |     |     ||     |     |     ||1",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "2||     |     |     ||     |     |     ||     |     |     ||2",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |3------------------4------------------5------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "3||     |     |     ||     |     |     ||     |     |     ||3",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "4||     |     |     ||     |     |     ||     |     |     ||4",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "5||     |     |     ||     |     |     ||     |     |     ||5",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |6------------------7------------------8------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "6||     |     |     ||     |     |     ||     |     |     ||6",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "7||     |     |     ||     |     |     ||     |     |     ||7",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         "8||     |     |     ||     |     |     ||     |     |     ||8",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " \---------------------------------------------------------/ ",
         "     0     1     2      3     4     5      6     7     8     ",
        ]

    expected_empty_output_cell_nums=\
        [\
         "     0     1     2      3     4     5      6     7     8     ",
         " /---------------------------------------------------------\ ",
         " |0------------------1------------------2------------------| ",
         " |0     1     2     |3     4     5     |6     7     8     || ",
         "0||     |     |     ||     |     |     ||     |     |     ||0",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |9     10    11    |12    13    14    |15    16    17    || ",
         "1||     |     |     ||     |     |     ||     |     |     ||1",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |18    19    20    |21    22    23    |24    25    26    || ",
         "2||     |     |     ||     |     |     ||     |     |     ||2",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |3------------------4------------------5------------------| ",
         " |27    28    29    |30    31    32    |33    34    35    || ",
         "3||     |     |     ||     |     |     ||     |     |     ||3",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |36    37    38    |39    40    41    |42    43    44    || ",
         "4||     |     |     ||     |     |     ||     |     |     ||4",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |45    46    47    |48    49    50    |51    52    53    || ",
         "5||     |     |     ||     |     |     ||     |     |     ||5",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |6------------------7------------------8------------------| ",
         " |54    55    56    |57    58    59    |60    61    62    || ",
         "6||     |     |     ||     |     |     ||     |     |     ||6",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |63    64    65    |66    67    68    |69    70    71    || ",
         "7||     |     |     ||     |     |     ||     |     |     ||7",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " |---------------------------------------------------------| ",
         " |72    73    74    |75    76    77    |78    79    80    || ",
         "8||     |     |     ||     |     |     ||     |     |     ||8",
         " ||     |     |     ||     |     |     ||     |     |     || ",
         " \---------------------------------------------------------/ ",
         "     0     1     2      3     4     5      6     7     8     ",
        ]




    def test_empty_board(self) :
        # Make empty board with all the labels
        got = labeled_board(None, want_cell_nums=True, want_num_possibles=True)
        self.assertEqual(got, Test_labeled_printer.expected_empty_output_cell_and_num_possible)

        # Make empty board with no extra labels
        got = labeled_board(None, want_cell_nums=False, want_num_possibles=False)
        self.assertEqual(got, Test_labeled_printer.expected_empty_output)

        # Make default empty board.
        # Should be: want_cell_nums=True, want_num_possibles=False)
        got = labeled_board()
        self.assertEqual(got, Test_labeled_printer.expected_empty_output_cell_nums)
        got = labeled_board(None, want_cell_nums=True, want_num_possibles=False)
        self.assertEqual(got, Test_labeled_printer.expected_empty_output_cell_nums)

    def test_caller_supplied_empty(self) :
        got = labeled_board( Board(), want_cell_nums=True, want_num_possibles=True )
        self.assertEqual(got, Test_labeled_printer.expected_empty_output_cell_and_num_possible)

    test_board = [\
          [0, 0, 6, 1, 0, 0, 0, 0, 8], 
          [0, 8, 0, 0, 9, 0, 0, 3, 0], 
          [2, 0, 0, 0, 0, 5, 4, 0, 0], 
          [4, 0, 0, 0, 0, 1, 8, 0, 0], 
          [0, 3, 0, 0, 7, 0, 0, 4, 0], 
          [0, 0, 7, 9, 0, 0, 0, 0, 3], 
          [0, 0, 8, 4, 0, 0, 0, 0, 6], 
          [0, 2, 0, 0, 5, 0, 0, 8, 0], 
          [1, 0, 0, 0, 0, 2, 5, 0, 0]
    ]
    test_board_output_cell_and_num_possibles = [\
          "     0     1     2      3     4     5      6     7     8     ",
          " /---------------------------------------------------------\ ",
          " |0------------------1------------------2------------------| ",
          " |0     1     2     |3     4     5     |6     7     8     || ",
          "0||     |     |  6  ||  1  |     |     ||     |     |  8  ||0",
          " ||4    |4    |     ||     |3    |3    ||3    |4    |     || ",
          " |---------------------------------------------------------| ",
          " |9     10    11    |12    13    14    |15    16    17    || ",
          "1||     |  8  |     ||     |  9  |     ||     |  3  |     ||1",
          " ||2    |     |3    ||3    |     |3    ||4    |     |4    || ",
          " |---------------------------------------------------------| ",
          " |18    19    20    |21    22    23    |24    25    26    || ",
          "2||  2  |     |     ||     |     |  5  ||  4  |     |     ||2",
          " ||     |3    |3    ||4    |3    |     ||     |4    |3    || ",
          " |---------------------------------------------------------| ",
          " |3------------------4------------------5------------------| ",
          " |27    28    29    |30    31    32    |33    34    35    || ",
          "3||  4  |     |     ||     |     |  1  ||  8  |     |     ||3",
          " ||     |3    |3    ||4    |3    |     ||     |5    |4    || ",
          " |---------------------------------------------------------| ",
          " |36    37    38    |39    40    41    |42    43    44    || ",
          "4||     |  3  |     ||     |  7  |     ||     |  4  |     ||4",
          " ||4    |     |4    ||4    |     |2    ||4    |     |4    || ",
          " |---------------------------------------------------------| ",
          " |45    46    47    |48    49    50    |51    52    53    || ",
          "5||     |     |  7  ||  9  |     |     ||     |     |  3  ||5",
          " ||3    |3    |     ||     |4    |3    ||3    |4    |     || ",
          " |---------------------------------------------------------| ",
          " |6------------------7------------------8------------------| ",
          " |54    55    56    |57    58    59    |60    61    62    || ",
          "6||     |     |  8  ||  4  |     |     ||     |     |  6  ||6",
          " ||4    |3    |     ||     |2    |3    ||5    |4    |     || ",
          " |---------------------------------------------------------| ",
          " |63    64    65    |66    67    68    |69    70    71    || ",
          "7||     |  2  |     ||     |  5  |     ||     |  8  |     ||7",
          " ||4    |     |3    ||3    |     |4    ||4    |     |4    || ",
          " |---------------------------------------------------------| ",
          " |72    73    74    |75    76    77    |78    79    80    || ",
          "8||  1  |     |     ||     |     |  2  ||  5  |     |     ||8",
          " ||     |4    |3    ||4    |3    |     ||     |2    |3    || ",
          " \---------------------------------------------------------/ ",
          "     0     1     2      3     4     5      6     7     8     ",
    ]

    def test_populated_board(self) :
        board = Board(Test_labeled_printer.test_board, None, "created by test_populated_board()", )
        got = labeled_board( board, want_cell_nums=True, want_num_possibles=True )
        self.assertEqual(got, Test_labeled_printer.test_board_output_cell_and_num_possibles)

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



