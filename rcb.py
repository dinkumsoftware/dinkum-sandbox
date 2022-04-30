#!/usr/bin/env python3
# dinkum/sudoku/rcb.py
''' Part of a sudoku Board.  An RCB represents a row/col/ or blk.
Each RCB is a [] of cells.
'''

# 2019-11-25 tc Moved fom sudoku.py
# 2019-12-07 tc Added unsolved_cells and unsolved_value_possibles
# 2019-12-12 tc Added a_cell_was_set() and remove_from_possibles()
# 2019-12-19 tc set as verb ==> solve
# 2019-12-22 tc Major redesign #3 
# 2019-12-23 tc redesign #3a.  remove unsolved_value_possibles
#               so don't have to maintain it incrementally
#               users build_unsolved_value_possibles() when
#               they need it.  Remove cell_possibles_changed()

from dinkum.sudoku      import * # All package wide def's
from dinkum.sudoku.cell import Cell, CellToSolve

class RCB(list) :
#diddle: xyzzy Sat 999035
#diddle: xyzzy Sat 999080
#diddle: xyzzy Sat 999088
#diddle: xyzzy Sat 999094
#diddle: xyzzy Sat 999100
#diddle: xyzzy Sat 999105
#diddle: xyzzy Sat 999111
#diddle: xyzzy Sat 999116
#diddle: xyzzy Sat 999122
#diddle: xyzzy Sat 999127
      initial_cell_placement  Should be called to initially populate the rcb
      a_cell_was_solved       Should be called when a cell in the rcb was solved
      remove_from_possibles   Removes a value as a possible solution
      build_unsolved_value_possibles constructs {} key: possible value
                                                   value: set of cells with value in possibles

      [x] gets/sets cells[x]
      iterators iterator over cells[]
    '''

    def __init__(self, rcb_type, board, rcb_num) :
        '''Creates an empty RCB
        rcb_type RCB_TYPE_ROW/COL/BLK
        board    The board we belong to
        rcb_num  Our index into board.row/col/blk

        We created all of these with no content.
        They are populated by calls to initial_cell_placement()

        self                     [] of our Cells
        unsolved_cells           set of cells in self that are not solved

        unsolved_value_possibles {} of sets of our cells 
                                 key: cell value
                                 value: set of our cells with key(cell value)
                                        as a possibility

        '''
        self.rcb_type = rcb_type
        assert self.rcb_type in ALL_RCB_TYPES, "Illegal rcb_type: %d" % self.rcb_type

        self.board = board

        self.rcb_num = rcb_num
        assert self.rcb_num in range(RCB_SIZE)

        # make a place for the cells themselves
        super().__init__( [None] * RCB_SIZE )

        # We currently don't have any cells, merely a place
        # to put them.  When populated via initial_cell_placement(),
        # the following will be populated with Cell values
        self.unsolved_cells = set()


    def initial_cell_placement(self, cell) :
        ''' Called to place cell in the RCB.
        The cell's indx into cell is retrieved from the cell
        The cell isn't touched, it is merely recorded as belonging
        to this RCB

        All other data structs are maintained.
        '''
        assert cell.value == Cell.unsolved_cell_value

        # For error messages
        id_str = "%s[%d] : cell#%d" % (RCB_NAME[self.rcb_type],
                                       self.rcb_num, cell.cell_num)
    
        # Figure out the index for cell into self[]
        (cell_rcb_num, indx) = cell.rcb_num_and_idx( self.rcb_type )

        assert self.rcb_num == cell_rcb_num, \
               "%s: rcb_num disagreement: rcb:%d, cell:%d" % (id_str,
                                                              self.rcb_num,
                                                              cell_rcb_num)
        # We don't allow overwrites
        assert self[indx] is None, "%s: Trying to overwrite cell#%d" % (id_str,
                                                                        self[indx].cell_num)
        
        # Put the cell in
        self[indx] = cell

        # and add it to unsolved
        self.unsolved_cells.add(cell)

    def a_cell_was_solved(self, solved_cell) :
        ''' Should be called when solved_cell (one of our cells,
        has been solved.

        Returns a set() of CellToSolve which should be solved
        as a result of the solving of solved_cell.

        Specifically:
            removes solved_cell from unsolved_cells
            calls remove_from_possibles(solved_cell.value)
            returning any cells that can be solved as a result
        '''
        # Enforce our assumptions
        assert solved_cell.is_solved()
        assert solved_cell in self.unsolved_cells

        solved_value = solved_cell.value  # What the solved_cell was set to

        # remove solved_cell from unsolved_cells
        self.unsolved_cells.remove(solved_cell)

        # Remove solved_cell.value as a possibility for all other
        # cells in our RCB.  Also rebuilds unsolved_value_possibles
        returned_set = self.remove_from_possibles( solved_value, solved_cell)

        # All done
        return returned_set


    def remove_from_possibles(self, value_or_values, except_cell_or_cells) :
        ''' Removes value_or_values as a possible solution for us.

        value_or_values can be a single value --or-- and iterable
        of values.

        except_cell_or_cells is a single Cell or iterable of Cells in
        this RCB that are excluded.  At least one must be
        provided. (Otherwise the RCB isn't solvable
        as no cell could provide value.)

        returns a (possibly empty) set of CellToSolve's that
        consists of any other Cell that becomes solvable
        by removing value as a possibility.

        if value isn't one of our possible_values, we
        silently return an empty set.

        The details:

        iterates thru unsolved_cells( sans except_cells )
             if cell.remove_from_possibles(values) removed something:
                 if 0 cell.possible_values left, assertion error    

        return set(CellToSolve)
        '''

        # Convert any non-iterable argument in an iterable
        # value?  or values?
        values = value_or_values # Assume it's iterable, ie values
        try:
            iter(value_or_values)
        except TypeError :
            values = [value_or_values] # wrong assumption, it was a single value
                                       # Make a single item iterable
        except_cells = except_cell_or_cells # Assume it's iterable, ie values
        try:
            iter(except_cell_or_cells)
        except TypeError :
            except_cells = [except_cell_or_cells] # wrong assumption, it was a single value
                                            # Make a single item iterable

        # Check our assumptions                                            
        for value in values :
            assert value in Cell.all_cell_values
        assert len(except_cells) > 0
        assert [ cell in self for cell in except_cells ]

        # What we return
        cells_to_solve = set()

        # iterates thru unsolved_cells sans except_cells
        #    Cell.remove_from_possibles(value)
        #    accumulates set(CellsToSolve)
        for cell in self.unsolved_cells :
            if cell not in except_cells :
                if cell.remove_from_possibles(values) :
                    # cell's possible_values changed
                    num_remaining_possibles = len(cell.possible_values)

                    # this would mean it could never be solved
                    assert (num_remaining_possibles != 0) 
                    
                    # Solvable?
                    if num_remaining_possibles == 1 :
                        # Yes, tell caller to solve it
                        sole_remaining_possible_value = list(cell.possible_values)[0]
                        cells_to_solve.add ( CellToSolve(cell, sole_remaining_possible_value ) )

        # Tell caller some solvable cells
        return cells_to_solve ;


    def unsolved_values(self) :
        ''' returns a set of values to be solved
        '''
        return Cell.all_cell_values - self.solved_values()


    def solved_values(self) :
        ''' returns set of values already solved
        '''
        return set ([ cell.value for cell in self.solved_cells() ])

    def solved_cells(self) :
        ''' set of cells that are solved
        '''
        return set([ cell for cell in self if cell.is_solved() ])


    def sanity_check(self) :
        ''' an RCB sanity check.

        Checks multiple conditions and asserts if they aren't met.
        '''

        # Used for error messages
        id_str = "%s[%d]" % (RCB_NAME[self.rcb_type], self.rcb_num)
        
        assert len(self) == RCB_SIZE,                                           \
            "%s: Wrong number of cells." % id_str

        # Look at each cell
        for idx in range(RCB_SIZE) :
            cell = self[idx] 

            # Make sure it exists
            assert isinstance( cell, Cell), "%s[%d]: Not populated." %(id_str, idx)
        

        # Verify the number of unsolved cells
        our_unsolved_cells = set()
        for cell in self :
            if not cell.is_solved() :
                our_unsolved_cells.add(cell)
        assert our_unsolved_cells == self.unsolved_cells

        # Verify unsolved_value_possibles
        our_unsolved_value_possibles = self.build_unsolved_value_possibles()

        # Need 1 value in our_unsolved_value_possibles for each unsolved cell
        assert  len(our_unsolved_value_possibles) ==  len(self.unsolved_cells)

        # All the cells in our_unsolved_value_possibles must be unsolved
        our_unsolved_cells = set()
        for (value,cells) in our_unsolved_value_possibles.items() :
            for cell in cells :
                our_unsolved_cells.add(cell)
        assert  self.unsolved_cells == our_unsolved_cells
        
        # solved_cells + unsolved_cells = all cells in rcb with no overlap
        self.solved_cells() | self.unsolved_cells == set(self)
        self.solved_cells() & self.unsolved_cells == set()

        # solved_values + unsolved_values = all possible values with no overlap
        self.solved_values() | self.unsolved_values() == Cell.all_cell_values
        self.solved_values() & self.unsolved_values() == set()


    def build_unsolved_value_possibles(self) :
        ''' Builds and returns a {} keyed by cell_value and whose value is
        a set() of cells in the rcb that can provide that cell_value.
        '''
        
        # what we return
        ret_unsolved_value_possibles = {}

        # Put any unsolved cell whose possible value
        # could be value in unsolved_value_possible[value]
        for cell in self.unsolved_cells :
            for value in cell.possible_values :
                if value in ret_unsolved_value_possibles :
                    ret_unsolved_value_possibles[value].add(cell)
                else :
                    # First time we have seen this value
                    # Create the set itself with cell as only member
                    ret_unsolved_value_possibles[value] = set ([cell])

        return ret_unsolved_value_possibles

    def unsolved_cells_with_common_unique_values(self, match_size) :
        '''
        Searches every rcb for pairs(match_size=2) and triples
        (match_size=3) of unsolved cells that all have the same
        possible value unique to those pairs/triples in this
        rcb i.e. no other cell in the rcb has that value as a possible.

        It works for match sizes other than 2 or 3, but probably
        not a lot of usefulness in the real world.

        returns [] of tuples:
            ( set(cells with those values as possible_values)
              set(values uniquely in common) 
            }
        '''

        # unsolved_value_possibles is a {} keyed by "cell value"
        # containing a set() of cells that have "cell value" in
        # their cell.possible_values

        # We iterate thru that looking for values where only
        # "match_size" cells have that value as a possible
        # We keep track of results in two dictionaries:
        #   matching_cells
        #   matching_values
        # Each is key'ed by a tuple of the matching Cell's cell #s
        # Their values are sets() of matching cells and the values
        # They have in commong
        # Note: we have to use cell#s rather than Cells
        #       as {} keys because tuple of Cells isn't hashable
        matching_cells  = {}
        matching_values = {}
        for (value, cells) in self.build_unsolved_value_possibles().items() :
            if len(cells) == match_size :
                # We've got a winner

                # Make tuple of the Cell#s of matching cells
                cell_nums = [ cell.cell_num for cell in cells ]
                cell_nums.sort()
                cell_nums = tuple(cell_nums)

                if cell_nums in matching_cells :
                    # We seen these cell's before
                    matching_values[cell_nums].add(value)
                else:
                    # First time we've seen these cells
                    matching_cells[cell_nums]   = cells
                    matching_values[cell_nums]  = set([value])

        # We now have to translate matching_cells/values
        # back to a list and return it
        # Each element in [] is a tuple(set(matching cells),
        #                               set(unique values they share))
        ret_list = []
        for (cells, values) in zip(matching_cells.values(), matching_values.values()) :
            ret_list.append( (cells, values) )

        return ret_list

    def other_rcbs(self, cell) :
        ''' Returns iterable of the RCBs of cell other
        than us.

        If cell doesn't have any rcbs, we return empty list.
        This generally only happens in unittest code.

        '''
        returned_list = []
        for rcb in [r for r in cell.rcbs if r != self ] :
            if rcb is not None and rcb is not self :
                returned_list.append(rcb)

        return returned_list

    def is_solved(self) :
        ''' Returns True if all cells have solved, i.e. have values '''
        return not self.unsolved_cells

    def name(self) :
        ''' Returns something like:
                row#4
        '''
        return "%s#%d" % (RCB_NAME[self.rcb_type], self.rcb_num)

    def __str__(self) :
        ''' Returns terse human-readable description. e.g.
                row#3: [3 ? 2 ... ]  
        ? ==> unsolved    Cell
        X ==> unpopulated Cell
        unsolved values are: ?
        unpolu
        '''
        # Describe outselves
        ret_str = "%s: [ " % self.name()

        # And each of our cells
        for cell in self :
            ret_str += cell.str_value(unsolved_char='?') if cell else 'X'
            ret_str += ' '

        # Close the list
        ret_str += ']'
        
        return ret_str
        
    def detailed_str(self) :
        ''' String representation.  Example:
            row[3]:
               Cell#s:   27 28 29 30 31 32 33 34 35 
               Indexs:    0  1  2  3  4  5  6  7  8
               Values:    6  _  _  8  _  4  _  _  5
               Possibles:
                          3  3        3     3  3
                             4  4  
                             6  6           6  6
               Cell index possibles for unsolved values:
                  1:  0 2 4 6 7 
                  2:  0 2
                  3:  4 6 7 
                  4:  0 2 4 6 7 
                  9:  4 6 7

        Unpopulated Cells are printed as X
        '''

        ret_str = '' # What we return

        # format stuff
        label_width = len("possibles:")  # longest label
        indent_str = " " * 3  # How much to indent all but first line
        col_width = 3 # how many spaces per cell/value/possible

        # Our type and such e.g.
        # row[3]:
        ret_str += "%s:\n" %  self.name()

        # What to output if there isn't a Cell, i.e. None
        non_cell_str = "XX"

        # Cell numbers on one line
        # non-Cells as 'XX' e.g.
        # Cell#s: 27 28 29 30 31 32 33 34 35 
        ret_str += indent_str + "%*s" % (label_width, "Cell#s:")
        for cell in self :
            ret_str += "%3d" % cell.cell_num if cell else ' ' + non_cell_str
        ret_str += '\n'

        # Cell indexes one line
        ret_str += indent_str + "%*s" % (label_width, "Indexs:")
        ret_str += "  0  1  2  3  4  5  6  7  8"       + '\n'

        # Cell values on one line
        # e.g.
        # Values:  6  _  _  8  _  4  _  _  5
        # non-Cell values as 'XX'
        ret_str += indent_str + "%*s" % (label_width, "Values:") # space over and label
        for cell in self :
            # position been populated ?
            if cell :
                # yes
                token = cell.str_value(col_width, '_')
            else :
                # Nope
                token = "%*s" % (col_width, non_cell_str)


            ret_str += token  # this cell's representation
        ret_str += '\n' # terminate the line

        # possibles of all the unsolved cells.
        # one line for each unsolved value, with
        # the value under the cell column
        # blanks for solved cells. e.g.
        # Possibles:
        #            3  3        3     3  3
        #               4  4  
        #               6  6           6  6

        ret_str += indent_str + "%*s" % (label_width,"Possibles:") + "\n"
        for value in Cell.all_cell_values :
            # Build a line to print
            possibles_line = indent_str + ' ' * label_width

            for cell in self :
                if cell is not None and value in cell.possible_values :
                    # value is a possible for this cell
                    possibles_line += "%*d" % (col_width, value)  # output it
                else :
                    possibles_line += ' ' * col_width  # all spaces
            possibles_line += '\n'

            # If there are some values to output, do so
            # suppress all blank line
            if not possibles_line.isspace() :
                # we have something to out
                ret_str += possibles_line
                    

        # This converts self.unsolved_value_possibles to human readable string, e.g
        #       Cell index possibles for unsolved values:
        #         1:  0 2 4 6 7 
        #         2:  0 2
        #         3:  4 6 7 
        #         4:  0 2 4 6 7 
        #         9:  4 6 7

        ret_str += self.str_unsolved_value_possibles(indent_str)

        # Give 'um the answer
        return ret_str


    def str_unsolved_value_possibles(self,
                                     indent_str = "") :
        '''
        # builds and returns unsolved_value_possibles
        # as a human readable string.  
        # 
        # The build unsolved_value_possibles is a
        # {} keyed by value whose {}value is set() of cells.
        #
        # Each line is prepended by indent_str.
        #
        # Example for 3 unsolved cells at index 2,4,6
        #      Cell index possibles for unsolved values:
        #         1:  2  4  6
        #         3:  4  6
        #         9:  2  4
        '''

        # Build unsolved_value_possibles
        unsolved_value_possibles=self.build_unsolved_value_possibles()

        # How much to index the 1: to 9: lines
        secondary_indent_str = indent_str + ' ' * 3

        ret_str = '' # what we return

        # Give them possible cells that satisfy unsolved values
        # Sort the indexes before we print them
        # e.g.               Cell index possibles for unsolved values:
        #                       1:  1  2  4  6  7 
        ret_str += "%sCell index possibles for unsolved values:\n" % (indent_str)

        # Build a [] of values in unsolved_value_possibles so we
        # can sort it an output values in numerical order
        our_unsolved_values = list ( unsolved_value_possibles.keys() )
        our_unsolved_values.sort()

        for value in our_unsolved_values :
            # Get the possible cells that provide this value
            cells = self.unsolved_value_possibles[value]

            ret_str += "%s%d: " % (secondary_indent_str, value)

            # Collect all the indexes of possible cells that
            # could supply value (whew!) in indexs
            indexs=[]
            for cell in cells:
                (rcb_num, rcb_idx) = cell.rcb_num_and_idx(self.rcb_type)
                indexs.append(rcb_idx)

            # Now sort and "print" it
            indexs.sort()
            for rcb_idx in indexs :
                ret_str += "%2s" % (rcb_idx)

            ret_str += '\n' # terminate the line

        # Give 'um the answer
        return ret_str

# Test code
import unittest
import dinkum.sudoku.board

class Test_rcb(unittest.TestCase):

    # un-test functions, i.e. support code
    def all_unsolved_rcb_for_test(self, rcb_type) :
        ''' For test purposes, constructs and returns
        an RCB populated with cells.  This is simulating what the Board
        constructor does, but we can't do that here because
        we end up with circular imports.

        All the cells in the returned rcb are unsolved.
        '''

        # Get the cell numbers we are going to assign
        # We'll do row 4 --or-- col 6 --or blk 2
        if rcb_type == RCB_TYPE_ROW :
            rcb_num = 4
            our_cell_nums = range (36, 45)
        if rcb_type == RCB_TYPE_COL :
            rcb_num = 6
            our_cell_nums = range ( 6, 87, 9)
        if rcb_type == RCB_TYPE_BLK :
            rcb_num = 2
            our_cell_nums = (list(range( 6,  9)) +
                             list(range(15, 18)) +
                             list(range(24, 27)) )
        
        # Make an unpopulated rcb
        rcb = RCB(rcb_type, None, rcb_num)

        # Populate it
        for cell_num in our_cell_nums :
            rcb.initial_cell_placement ( Cell(None, cell_num))

        # Make sure life is good
        rcb.sanity_check()

        return rcb

    def all_solved_rcb_for_test(self, rcb_type) :
        ''' returns an rcb with every cell having a value.
        '''
        # Start with one with nothing solved
        rcb = self.all_unsolved_rcb_for_test(rcb_type)

        for (indx, value) in zip( range(RCB_SIZE),             # index
                                  [5, 2, 9, 6, 1, 3, 8, 4, 7] # value
                                  ) :
            # Adust the cell
            cell = rcb[indx]
            cell.value = value
            cell.possible_values=set()

        # Adjust our self
        rcb.unsolved_cells = set()
        rcb.unsolved_value_possibles = rcb.build_unsolved_value_possibles()

        # Make sure life is good
        rcb.sanity_check()

        return rcb


    def partially_solved_rcb_for_test(self, rcb_type, not_solved_indexes) :
        ''' returns a board with some cells solved and others unknown.
        not_solved_indexes is an iterable of cell indexes (0-8) that are NOT solved
        '''
        # Get a full one
        rcb = self.all_solved_rcb_for_test(rcb_type)
        assert len(rcb.unsolved_cells) == 0  # All should have a value

        # Go thru and "unset" what the caller specifies
        # Two passes

        # On first pass go thru and accumulate the values
        # of all the cells we are going to unset
        unsolved_cell_values = set()
        for indx in not_solved_indexes :
            cell = rcb[indx]

            # build our possibles
            unsolved_cell_values.add ( cell.value )

        # Pass two. Solve what we need to.
        # Diddle the cells. We assume all unsolved cells could have any of those values
        # mark the cell unsolved in the rcb
        for indx in not_solved_indexes :
            cell = rcb[indx]

            # adjust the cell
            cell.value = Cell.unsolved_cell_value
            cell.possible_values |= unsolved_cell_values

            # adjust rcb
            rcb.unsolved_cells.add ( cell )
        

        # Rebuild unsolved_value_possibles
        rcb.unsolved_value_possibles = rcb.build_unsolved_value_possibles()

        # Make sure life is good
        rcb.sanity_check()
        return rcb

    # Actual test functions
    def test_construction(self) :
        rcb = RCB(RCB_TYPE_BLK, None, 2) 

        # All should be empty
        # and tests __getitem__()
        for idx in range(RCB_SIZE) :
            self.assertEqual( rcb[idx], None )

    def test_bad_rcb_type(self) :
        bad_rcb_value = 82
        
        try:
            self.assertRaises( RCB(bad_rcb_value, None, 2))
        except AssertionError as exc :
            self.assertEqual(str(exc), "Illegal rcb_type: 82")

        def test_iteration(self) :
            rcb = RCB(RCB_TYPE_COL, None, 4)

            self.assertEqual( len(rcb), RCB_SIZE )

            # All cells should be uninitialized
            cell_cnt = 0
            for c in rcb :
                self.assertNone, c.value
                cell_cnt += 1

            self.assertEqual( cell_cnt, len(rcb) )

    def test_solved_cells(self) :
        # an empty rcb should have none solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_cells(), set() )
        
        # a full rcb should have all cell solved
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_cells(), set(rcb) )

        # a partial rcb should have some
        solution_rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)

        # rcb is subset of solution_rcb with [8,4,3] not solved
        cells_unsolved = [8,4,3]
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_ROW,
                                                 cells_unsolved)
        solved_should_be = set(rcb) - set ([ rcb[indx] for indx in cells_unsolved ])

        self.assertEqual ( rcb.solved_cells(), solved_should_be )

        

    def test_solved_values(self) :
        # an empty rcb should have no values in solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_values(), set() )

        # a full rcb should have all values in solved
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_values(), Cell.all_cell_values )


        # a partial rcb should have some
        solution_rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)

        # rcb is subset of solution_rcb with [1,2,4,6] not solved
        cells_unsolved = set([  1,2,  4,   6       ])
        cells_solved   = set([0,    3,  5,   7, 8, ])
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_ROW,
                                                 cells_unsolved)

        solved_should_be = set([ rcb[indx].value for indx in cells_solved])
        self.assertEqual ( rcb.solved_values(), solved_should_be )


    def test_unsolved_values(self) :

        # an empty rcb should have every value in unsolved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.unsolved_values(), Cell.all_cell_values )

        # a full rcb should have no values in unsolved
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.unsolved_values(), set() )


        # a partial rcb should have some
        solution_rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)

        # rcb is subset of solution_rcb with [4,5,7,8] not solved
        cells_unsolved = [4,5,7,8]
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_ROW,
                                                 cells_unsolved)
        unsolved_should_be = set([ solution_rcb[indx].value for indx in cells_unsolved])
        self.assertEqual ( rcb.unsolved_values(), unsolved_should_be )


    def test_other_rcbs(self) :
        board = dinkum.sudoku.board.Board() # empty board

        # Try a row
        rcb = board.rows[3]
        cell = rcb[5]   # board[3][5]   blk 4
        self.assertEqual (rcb.other_rcbs(cell), [ board.cols[5], board.blks[4] ] )

        # Try a col
        rcb = board.cols[3]
        cell = rcb[2]   # board[2][3]   blk 1
        self.assertEqual (rcb.other_rcbs(cell), [ board.rows[2], board.blks[1] ] )

        # Try a blk
        rcb = board.blks[8]
        cell = rcb[2]   # board[6][8]   blk 8
        self.assertEqual (rcb.other_rcbs(cell), [ board.rows[6], board.cols[8] ] )


    def test_sanity_check(self) :
        # We want trigger all the bad conditions it checks for

        # wrong # of cells
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_ROW)
        rcb.pop()
        self.assertRaises(AssertionError, rcb.sanity_check )

        # wrong number of unsolved cells
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_COL)
        rcb.unsolved_cells.pop()
        self.assertRaises(AssertionError, rcb.sanity_check )

        # unpopulated cell
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_COL)
        rcb[8] = None
        self.assertRaises(AssertionError, rcb.sanity_check )

        # a populated cell is solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        rcb[4].value = 3 # solve it
        self.assertRaises(AssertionError, rcb.sanity_check )


    def test_name(self) :
        rcb = RCB(RCB_TYPE_ROW, None, 2)
        self.assertEqual ( rcb.name(), "row#2")

        rcb = RCB(RCB_TYPE_COL, None, 4)
        self.assertEqual ( rcb.name(), "col#4")

        rcb = RCB(RCB_TYPE_BLK, None, 8)
        self.assertEqual ( rcb.name(), "blk#8")

    
    def test_str(self) :
        # An unpopulated row
        rcb = RCB(RCB_TYPE_ROW, None, 5)
        self.assertEqual( str(rcb),
                          "row#5: [ X X X X X X X X X ]")

        # A partially populated column
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL, [1,6,8])
        self.assertEqual( str(rcb),
                          "col#6: [ 5 ? 9 6 1 3 ? 4 ? ]")



    def test_detailed_str(self) :
        # An unpopulated RCB
        rcb = RCB(RCB_TYPE_BLK, None, 8)
        should_be = '\n'.join([
            "blk#8:",
            "      Cell#s: XX XX XX XX XX XX XX XX XX",
            "      Indexs:  0  1  2  3  4  5  6  7  8",
            "      Values: XX XX XX XX XX XX XX XX XX",
            "   Possibles:",
            "   Cell index possibles for unsolved values:",
            ]) + '\n'
        self.assertEqual( rcb.detailed_str(), should_be)


        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL, [2, 7])        

        should_be = '\n'.join( [
            "col#6:",
            "      Cell#s:  6 15 24 33 42 51 60 69 78",
            "      Indexs:  0  1  2  3  4  5  6  7  8",
            "      Values:  5  2  _  6  1  3  8  _  7",
            "   Possibles:",
            "                     4              4   ",
            "                     9              9   ",
            "   Cell index possibles for unsolved values:",
            "      4:  2 7",
            "      9:  2 7"
        ]) + '\n'
        self.assertEqual( rcb.detailed_str(), should_be)



    def test_a_cell_was_solved(self) :
        # Get a partially populated rcb with index 3,4,5 unsolved
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL, [3,4,5])

        # Initial:
        # col[6]:
        # Cell#s:  6 15 24 33 42 51 60 69 78
        # Indexs:  0  1  2  3  4  5  6  7  8
        # Values:  5  2  9  _  _  _  8  4  7
        # Cell index possibles for unsolved values:
        # 1:  3  4  5 
        # 3:  3  4  5 
        # 6:  3  4  5 

        # Can't solve a previously solved Cell
        already_solved_cell = rcb[0]
        self.assertRaises (AssertionError, rcb.a_cell_was_solved, already_solved_cell )
        
        # Can't do this with a cell not in the RCB
        non_rcb_cell = Cell(None, 80)
        self.assertRaises (AssertionError, rcb.a_cell_was_solved, non_rcb_cell )

        # Can't do this with unsolved cell
        unsolved_cell = rcb[3]
        self.assertRaises( AssertionError, rcb.a_cell_was_solved, unsolved_cell )

        # Test if it actually works
        # Set one of our unsolved cells to an unsolved value
        solved_cell  = rcb[3]
        solved_value = 1
        solved_cell.solve(solved_value)

        # After rcb[3] solved to 1
        # col[6]:
        # Cell#s:  6 15 24 33 42 51 60 69 78
        # Indexs:  0  1  2  3  4  5  6  7  8
        # Values:  5  2  9  1  _  _  8  4  7
        # Cell index possibles for unsolved values:
        # 3:  4  5 
        # 6:  4  5 

        ret_set = rcb.a_cell_was_solved(solved_cell)
        self.assertEqual (ret_set, set() ) # No other cells can be solved
                                           # as a result of this
        # cell is no longer unsolved
        self.assertEqual (rcb.unsolved_cells, set([ rcb[4], rcb[5] ]))

        # No one can provide it's value
        self.assertTrue (solved_cell.value not in rcb.build_unsolved_value_possibles())

        # Cell can't provide any other value
        for cells in rcb.build_unsolved_value_possibles().values() :
            self.assertTrue( solved_cell not in cells )

        rcb.sanity_check()

        # Solved another our unsolved cells to an unsolved value
        solved_cell  = rcb[4]
        solved_value = 3
        solved_cell.solve(solved_value)

        # After rcb[4] solved to 4
        # col[6]:
        # Cell#s:  6 15 24 33 42 51 60 69 78
        # Indexs:  0  1  2  3  4  5  6  7  8
        # Values:  5  2  9  1  3  _  8  4  7
        # Cell index possibles for unsolved values:
        # 6:  5 
        # Note that cell rcb[5] can be solved to 6

        ret_set = rcb.a_cell_was_solved(solved_cell)

        # We know that cell at rcb[5] can be set to 6
        should_be = set([ CellToSolve(rcb[5], 6) ])
        self.assertEqual (ret_set, should_be )

        # cell is no longer unsolved
        self.assertEqual (rcb.unsolved_cells, set([ rcb[5] ]))

        # No one can provide it's value
        self.assertTrue (solved_cell.value not in rcb.build_unsolved_value_possibles())

        # Cell can't provide any other value
        for cells in rcb.build_unsolved_value_possibles().values() :
            self.assertTrue( solved_cell not in cells )

        rcb.sanity_check()


    def test_remove_from_possibles(self) :
        # Note: Most of the actual operation testing is in
        #       test_a_cell_was_solved().  It was too hard
        #       to manually put the rcb in the right position

        # Error conditions
        # Bad value
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertRaises (AssertionError, rcb.remove_from_possibles,18, [ rcb[4] ] )

        # Silently don't remove non-existent values
        # just returns empty set
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)
        ret = rcb.remove_from_possibles( 5,  [rcb[0], rcb[3]] )
        self.assertEqual ( ret,                          set() )
        self.assertEqual ( rcb.unsolved_value_possibles, {}    )
        rcb.sanity_check()

        # Remove a possiblity that doesn't cause any other cells to be solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)  # empty
        removed_value = 4
        ret = rcb.remove_from_possibles( removed_value, [rcb[indx] for indx in range(3)])

        self.assertEqual ( ret, set() )
        rcb.sanity_check()
        




if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
