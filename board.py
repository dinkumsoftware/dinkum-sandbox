#!/usr/bin/env python3
# dinkum/sudoku/board.py
''' Defines sudoku Board class which represents a
sudoku board full of Cells with values.
'''
#diddle: xyzzy Sat 060476
#diddle: xyzzy Sat 060521
#diddle: xyzzy Sat 060529
#diddle: xyzzy Sat 060534
#diddle: xyzzy Sat 060539
#diddle: xyzzy Sat 060545
#diddle: xyzzy Sat 060550
#diddle: xyzzy Sat 060555
#diddle: xyzzy Sat 060560
#diddle: xyzzy Sat 060565
# 2019-12-10 tc copy_construtor.  Use name of copied board
#               Added reduce_possibles_from_matching_cells()
# 2019-12-14 tc Added a_cell_was_set() and
#               solve_cells()
# 2019-12-16 tc Solved the saturday globe
# 2019-12-19 tc set as verb ==> solve
# 2019-12-19 tc Major redesign #3: __eq__ also tests cell.possible_values
#                                  solve() stops when no board changes
# 2019-12-23 tc redesign #3.a RCB.unsolved_cell_possibles removed
#                             so don't maintain it incremental.
#                             use RCB.build_unsolved_cell_possibles()
#                             when needed.
# 2020-02-01 tc Went to exhaustive trials

from dinkum.sudoku.rcb   import *
from dinkum.sudoku.cell  import *
from dinkum.sudoku.stats import *

import time

def str_to_list_of_rows(s) :
    ''' translate s to list of row-lists suitable for input to Board()
    and return it.

    s should contain a boards worth (81) of digits in range 0-9 inclusive.
    Whitespace is ignored as well as any non-digits.  The values are in
    raster order.

    Not much error checking is done. Presumably someone else is
    error checking the returned list of row-lists.

    Raises ExcBadStrToConvert if there aren't exactly a boards worth of
    digits in s.
    '''

    # Disappear the white space
    digits = [ int(c) for c in s if c.isdigit() ]

    # Verify the count
    if len(digits) != (RCB_SIZE)*(RCB_SIZE) :
        raise ExcBadStrToConvert  # Oops

    # Put them in their place
    list_of_rows=[]
    for row_num in range(RCB_SIZE) :
        offset = row_num * RCB_SIZE # which digit starts this row
        list_of_rows.append ( digits[offset:offset+RCB_SIZE] )

    return list_of_rows


class Board :
    ''' Holds the representation of of a sudoku board.
    Has a solve() which will solve the Board by altering
    it in place.

    Various data:
      name            Name of the board, set in constructor
      description     Description of the board, set in constructor
    

      cells           List of all Cells in raster order,
                      i.e. left to right, top to bottom
      unsolved_cells  Set of Cells that need to be filled in with a value

      rows,cols,blks  [] of Cells in that entity.  Indexed by {row/col/blk}_num
                      Can be retrieved by rcb()

      rcbs            [] of all rows,cols,blks

      solve_stats     class Stats that holds various
                      statistics about solve(), e.g.
                      how long to solve, etc

    Board()[row][col] can be used to get Cell at (row,col)

    Some useful functions (there are others)
      solve()              Trys to solve the board with guessing
      solve_by_deduction() Trys to solve the board without guessing
      solve_cells          solves(sets) a bunch of cells

    A Board can be specified to Board() as a list of row, e.g
        [ [1,2,3,4,5,6,7,8,9],
          [0,0,1,0,0,2,5,0,0],
               ...
        ]
    It can also be specified as a string of digits 0-9 separated by as
    much or little whitespace as you desire. e.g.
        1 2 3 4 5 6 7 8 9
        0 0 1 0 0 2 5 0 0
            ...
    --or--
        123456789001002500
            ...

    It can also be passed another Board, i.e. copy constructor
    '''

    # Class variables
    board_copy_cnts = {} # How many times a board was copied in
                         # in copy constructor.
                         # key: base board name value: # times copied
                         # see _pick_name_and_desc()


    def __init__(self, board_spec=None, name=None, desc="") :
        ''' constructor of a Board
        board_spec is list of row-lists --or--
        a string of values              --or--
        a Board
        If board_spec is None, an empty board will be created.

        name is used as the name of the board.
        If name is None, a unique name will be chosen, something on
        the order of:
            board-<lots of numbers which represent the curr time> 

        desc is description of the board, i.e. it's source or
        characteristics.  It defaults to empty string.

        raise ExcBadPuzzleInput if "arr" is bad
        various assertion failures if things aren't right.
        '''

        # Deal with the name/description and statistics
        (self.name, self.description) = self._pick_name_and_desc(name, desc, board_spec)
        self.solve_stats  = Stats()
        
        # Convert board_spec into list of rows
        # Need to translate string into list of rows?
        if isinstance(board_spec, str) :
            try:
                list_of_rows = str_to_list_of_rows(board_spec)
            except ExcBadStrToConvert :
                raise ExcBadPuzzleInput( "Not an exact boards worth of digits in arr as string" )

        # Need to translate Board into list of rows?
        elif isinstance(board_spec, Board) :
            list_of_rows = board_spec.output()
        else :
            list_of_rows = board_spec

        # We are generating new board from a list of row-lists
        # We create empty data structs and have set() adjust them

        # Create all rows/cols/blocks.  Make them empty
        self.rows = [ RCB(RCB_TYPE_ROW, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 
        self.cols = [ RCB(RCB_TYPE_COL, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 
        self.blks = [ RCB(RCB_TYPE_BLK, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 

        # Gather them all in one place
        self.rcbs = self.rows + self.cols + self.blks

        # List of all Cells indexed by cell#
        # Is inited to unsolved and all values possible
        # We pass our self in so Cell knows what board it belongs to
        # Cell() initializes the rows/cols/blks it belongs to
        # These are created in raster order
        self.cells = [ Cell(self, cell_num) for cell_num in range(NUM_CELLS)]

        # A separate Set of Cells that are unsolved.
        # Currently all cells are unsolved
        # Note: We use Set rather than list because set is faster than []
        self.unsolved_cells = set(self.cells)
        assert len( self.unsolved_cells) == NUM_CELLS

        # Populate all rows/cols/blocks
        for cell in self.cells :
            # Populate all the rows/cols/blks that this cell belongs to
            self.rows[cell.row_num].initial_cell_placement(cell)
            self.cols[cell.col_num].initial_cell_placement(cell)
            self.blks[cell.blk_num].initial_cell_placement(cell)

        # We have a valid empty board at this point
        # Sanity check all the RCBs
        for rcb in self.rcbs :
            rcb.sanity_check() 

        # Is there any input to solve cells with?
        if not list_of_rows :
            return # nope, all done

        # We need to populate it with values as spec'ed by the caller

        # Go thru and solve each cell value from our input,
        # solve() adjusts all the data structures
        if len(list_of_rows) != RCB_SIZE :    # Sanity check input
            raise ExcBadPuzzleInput( "Wrong number of rows: %d" % len(list_of_rows) )

        cell_num=0
        row_num =0
        for row in list_of_rows :
            # Sanity check
            if len(row) != RCB_SIZE :
                raise ExcBadPuzzleInput( "Row %d: Wrong size: %d" % (row_num, len(row)))

            col_num = 0
            for value in row :
                # who we are testing
                cell=self.cells[cell_num]
                
                # Skip unknown values, all data bases init'ed for all unknown
                if value != Cell.unsolved_cell_value:
                    # Sanity check the value
                    if value not in Cell.all_cell_values :
                        raise ExcBadPuzzleInput( "Bad value: %d at (row,col) (%d,%d)" % (value, row_num, col_num))

                    # Common error msg for duplicate entries, which Should be formated with
                    # (cell_num, row_num, col_num, value, "row/col/blk"
                    err_fmt_str = "cell#%d at (%d,%d) value:%d is duplicated in cell's %s"

                    # We know that cell is currently unsolved
                    assert cell.value == Cell.unsolved_cell_value

                    # Can't have duplicate values in a row/col/blk
                    if value in [ cell.value for cell in cell.row] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "row"))
                    if value in [ cell.value for cell in cell.col] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "col"))
                    if value in [ cell.value for cell in cell.blk] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "blk"))

                    # All looks good, solve it
                    self.solve_a_cell(cell, value)

                cell_num += 1
                col_num += 1
            row_num += 1



        # Sanity check(s) A whole bunch of asserts
        # Could move this into unittest code....
        # but we aren't time sensitive at construction time
        self.sanity_check()

    def _pick_name_and_desc(self, name, desc, board_spec) :
        ''' returns tuple: (board_name, board_description)
        name, desc, board_spec should be the arguments passed
        into the constructor.

           board_name        name                   if name not None
                             board_spec.name-cp.<N> if board_spec is Board
                             board-<N>              otherwise.

           board_description desc                   if not None
                             board_spec.description if board_spec is Board
                             ""                     otherwise
        '''

        # What we return
        board_name = None
        board_desc = None

        # Pick the name
        if name :
            board_name = name
        elif isinstance(board_spec, Board) :
            # We keep track of the number of times a board
            # is copied in class variable: board_copy_cnts
            # a {} key:base board name value:# of times it is copied
            bn   = board_spec.name        # Just make the code read easier
            cp_dict = Board.board_copy_cnts
            if bn in  cp_dict :
                cp_dict[bn] += 1
            else:
                cp_dict[bn] = 1    # First copy

            # How many times this board has been copied
            copy_cnt = cp_dict[bn]

            # Pick the name
            board_name = board_spec.name + "-cp." + str(copy_cnt)

        else :
            board_name = self._unique_board_name()

        # Pick the description
        if desc :
            board_desc = desc
        elif isinstance(board_spec, Board) :        
            board_desc = board_spec.description
        else :
            board_desc = ""

        # All done
        return (board_name, board_desc)


    def solve(self) :
        '''
        Returns a Board that solve us.
        Return None if unsolvable
        raise Exception on multiple solutions 

        If we can't solve the board via solve_by_deduction()
        We try all possibles combinations.

        We change our values in the process
        Sets various statistics in solve_stats

        Our algorithm:

        solve()
            solve_by_deduction(), return on success

            cell_num = most_constrained_cell_num()
                     # pick unsolved cell with fewest possibles
                     # if more than one
                     #     break tie with lowest total unsolved in RCB
                     # if still more than one
                     #     pick the first

           # Try all possibles
           solve_results = []
           for v in cell.possible_values
               b=Board(self) # copy
               b.cells[cell_num].set(v)
               solve_results.append( b.solve() )  # recurse

           if all unsolved
              return unsolvable
           if 1 solved
              self = b
              return solved
           if >1 solved
              return/raise multiple solutions
        '''
        
        return self.solve_by_deduction() ######################################

        # Try to solve using logic
        bd = self.solve_by_deduction()
        if bd :
            # We did
            return bd

        # We are currently unsolved
        # Pick the cell with fewest choices
        mc_cell_num = self.most_constrained_cell_num()

        # and try all possibles values for that cell
        # We have to try all values to detect multiple solutions
        solve_results = []
        for value in self.cells[mc_cell_num].possible_values :
            bd = Board(self) # Make a copy
            bd.cells[mc_cell_num].solve(value)  # Put in value we are trying
            
            # Recurse and remember results
#           solve_results.append( (bd, bd.solve() ) )

        ######################################

        # Unsolvable
        # <todo> may not get here
        return None


    def solve_by_deduction(self) :
        '''
        Returns a Board that solve us.
        Return None if unsolvable
        raise Exception on multiple solutions 
        Solution attempt involves no guessing.
        We change our values in the process
        Sets various statistics in solve_stats
        '''

        # fractional seconds
        self.solve_stats.solve_start_time_secs = time.perf_counter()

        # We try all the solution techniques we know about
        # until board is solved.
        # We break out of the loop and give up when the
        # a cell wasn't solved in pass and board isn't changed in a pass
        self.solve_stats.num_solve_passes = 0
        while not self.is_solved() :

            # Snapshot the board state
            num_solved_this_pass = 0
#################################            board_on_last_pass = Board(self)
            board_on_last_pass = copy.deepcopy(self)

            # count the # of times thru the loop
            self.solve_stats.num_solve_passes += 1

            # Solve cells with only 1 possible value
            num_solved_this_pass += self.solve_cells_with_single_possible_value()

            # Solve row/col/blks where an unsolved value can only be
            # satisfied by a single cell
            num_solved_this_pass += self.solve_rcbs_with_single_possible_value_solution()

            # Remove some possibles by looking for matching cells with same possibles
            # and projecting that into other rcb's.  This doesn't actually solve any
            # cells, but may modifify the board
            num_solved_this_pass += self.solve_possibles_from_matching_cells()

            # Time to bail out?
            if num_solved_this_pass == 0   and   self == board_on_last_pass :
                break # too bad

        # All done, Remember how long we ran
        self.solve_stats.solve_time_secs = (time.perf_counter() -
                                            self.solve_stats.solve_start_time_secs)

        # Tell um how we did
        return self if self.is_solved() else None

    
    def solve_cells_with_single_possible_value(self) :
        '''Solves all unsolved cells on the board that have a single possible value.
        Returns number of cells solved.
        '''

        # Examine all the unsolved cells, looking for ones
        # that have only 1 possible solutions
        cells_to_solve = set() # Put those cells in this set
        for cell in self.unsolved_cells :
            if len(cell.possible_values) == 1 :
                # Extract the only element in the set.  Leave num_possible_values intact
                # See https://stackoverflow.com/questions/20625579/access-the-sole-element-of-a-set
                [value] = list(cell.possible_values)

                # and solve that value into the set of CellToSolve
                cells_to_solve.add( CellToSolve(cell, value) )


        # solve all those Cells (and any other Cells that solution causes)
        # return the total number solved
        return self.solve_cells( cells_to_solve )

    def solve_rcbs_with_single_possible_value_solution(self) :
        ''' solves all cells in all unsolved RCBs that 
        where an unsolved value can only be satisfied by a single cell (that cell)

        Returns number of cells that were solved
        '''
        num_solved = 0 # what we return

        # Iterate over unsolved rcbs
        for rcb in [rcb for rcb in self.rcbs if not rcb.is_solved()] :

            # Build a set() of CellToSolve's that could provide "value"
            # We build the list and then Cell.solve() in a separate pass
            # to prevent "dictionary changed size during iteration"
            cells_to_solve = set()
            unsolved_value_possibles = rcb.build_unsolved_value_possibles()
            for (value, possible_cells) in unsolved_value_possibles.items() :
                num_possibles = len(possible_cells)

                # if there is a value with solving cells,
                # something is broken as cell can't be solved
                assert num_possibles != 0

                # If there is only one such cell ....
                if num_possibles == 1 :
                    # We have a winner
                    # This is the only cell in the RCB what can provide "value"
                    # Extract the only element in the set, which is the providing cell
                    # See https://stackoverflow.com/questions/20625579/access-the-sole-element-of-a-set
                    [cell] = possible_cells

                    # Put it in set() to be solved
                    cells_to_solve.add( CellToSolve(cell, value))

                    
            # Now solve those cells
            num_solved += self.solve_cells( cells_to_solve )
                    
        # Tell um how we did
        return num_solved


    def solve_possibles_from_matching_cells(self) :
        '''
        Searches every rcb for pairs and triples
        of unsolved cells that all have the same possible value
        that is unique to that rcb, i.e. no other cell in the rcb
        has that value as a possible.

        Remove non-matching values from the pair/triple

        Remove matching values from any common rcb in
        the pair.

        It solves any Cells that become solvable as a result
        of this call.

        returns the number of solved cells
        '''

        for rcb in self.rcbs :
            # this looks for pairs and triples
            # Note: quads could happen, but they can't
            #       be in the same rcb, except us
            #       and there are no other unsolved
            #       cells with their value
            cells_to_solve = set() # Where we accumulate what to solve
            for match_size in [3, 2] :  # triples first, as they will include a pair
                # returns [] of tuples: (set() of matching cells
                #                        set() of values_uniquely_in_common)
                cells_and_values = rcb.unsolved_cells_with_common_unique_values(match_size)

                for (matching_cells, matching_values) in cells_and_values :
                    # Remove non-matching values from the pair/triple
                    # This is set of all other cells in the rcb that didn't
                    # match.  We will exclude them from remove_from_possibles() which
                    # makes remove_from_possibles() only operate on the pair/triple
                    except_cells = set(rcb) - matching_cells 

                    # Remove matching values from any common rcb in
                    # the pair/triple
                    assert len(matching_cells) == match_size

                    # Iterate thru a list of rcbs that the matching cells have in common
                    first_cell = list(matching_cells)[0]  # get an arbitary cell out of the set

                    for common_rcb in first_cell.common_rcbs( matching_cells ) :
                        cells_to_solve |= common_rcb.remove_from_possibles(matching_values, matching_cells)

        # Now solve the Cells we found
        # and tell them how many we solved
        return self.solve_cells(cells_to_solve)

    def most_constrained_cell_num(self) :
        ''' Returns the unsolved cell_num with the fewest choices.
        The algorithm:
            pick unsolved cell with fewest possibles
            if more than one
                break tie with lowest total unsolved in RCB
                if still more than one
                     pick the first
        '''
        
        default_answer = 0 # cell# 0

        # sanity check
        if self.is_solved() :
            return default_answer

        # pick unsolved cell with fewest possibles
        unsolved_cells = list(self.unsolved_cells)  # set ==> list

        # sorting functions
        def by_cell_num(cell) :
            return cell.cell_num
        def by_num_possibles(cell) :
            return len(cell.possible_values)
        
        # Put fewest possibles at head of the list
        unsolved_cells.sort( key=by_cell_num)        # put in cell num order
        unsolved_cells.sort( key=by_num_possibles)   # now sort by # possibles

        # Eliminate all but those with fewest possible values
        min_num_possibles = len( unsolved_cells[0].possible_values)
        for (indx, cell) in enumerate( unsolved_cells ) :
            if indx == 0 :
                continue  # skip the first one

            if len(unsolved_cells[indx].possible_values) > min_num_possibles :
                # Remove this cell and all following
                unsolved_cells = unsolved_cells[:indx]
                break


        # unsolved_cells has all the cells with minimum number of possible values
        if len(unsolved_cells) == 1 :
            # only one choice, we are done
            return unsolved_cells[0].cell_num


        # We have multiple cells with same number of possible_values
        # First tie breaker.. The minimum sum of unsolved cells RCB
        # Build a list of (cell, sum_of_rcb_unsolved)
        unsolved_rcb_cnt = []
        for c in unsolved_cells :
            urc = 0  # count of unsolveds
            for rcb in c.rcbs :
                urc += len(rcb.unsolved_cells)
            unsolved_rcb_cnt.append( (c, urc) )

        # Find put minimum at head of the list
        def by_rcb( t ) : return t[1]
        unsolved_rcb_cnt.sort (key=by_rcb)


        # If there is only one cell left we return it
        # If there are multiple cells left, we return the first
        # Both are the same
        return unsolved_rcb_cnt[0][0].cell_num

    def __getitem__(self, row) :
        ''' Returns our RCB at row
            Allows Board()[row][col] to return a cell
        '''
        return self.rows[row]

    def rcb(self, rcb_type) :
        ''' Return [] of RCBs, rows[], cols[], or blks[]
        depending on rcb_type
        '''

        if   rcb_type == RCB_TYPE_ROW :
            return self.rows
        elif rcb_type == RCB_TYPE_COL :
            return self.cols
        elif rcb_type == RCB_TYPE_BLK :
            return self.blks
        else :
            assert False, "Unknown rcb_type:" + str(rcb_type) + " Should be one of:" + str(ALL_RCB_TYPES)
        assert False, "Impossible place"


    def solve_cells( self, cells_to_solve ) :
        ''' All Cells in cells_to_solve will
        be solved, along with any Cells that
        become solvable as a result of
        solving one of the cells in cells_to_solve.

        cells_to_solve should be iterable containing
        CellToSolve's (class holds a Cell and a value
        to solve it with)

        Returns the total number of cell's solved.

        Cells in cells_to_solve which have already
        been solved are silently ignored as long
        as they have been solved with passed in
        value in CellToSolve
        '''
        # What we return
        num_solved = 0

        # What we learn from solving a cell.
        additional_cells_to_solve = set()

        for (cell,value) in cells_to_solve :
            if cell.is_solved() :
                # Already solved, make sure values match
                assert cell.value == value
            else :
                # cell not solved, put on list to solve
                additional_cells_to_solve |= self.solve_a_cell(cell, value)
                num_solved += 1

        # Any more to solve?
        if additional_cells_to_solve :
            # Yes, Recurse
            num_solved += self.solve_cells( additional_cells_to_solve )

        # All done
        return num_solved
        

    def solve_a_cell(self, cell, value) :
        ''' solves cell with value.

        Returns a set(CellToSolve) that can be solved
        as a result of solving cell

        Specifically
            cell.solve(value)
            remove cell from unsolved
            for rcb in cell.rcbs()
                set(CellToSolve) |= RCB.a_cell_was_solved(cell)
            return set(CellToSolve)
        '''

        # Actually solve the cell itself
        cell.solve(value)

        # remove cell from unsolved_cells
        assert cell in self.unsolved_cells
        self.unsolved_cells.remove(cell)

        # What we return
        cells_to_solve = set()

        # Iterates thru rcbs:        
        for rcb in cell.rcbs :
            cells_to_solve |= rcb.a_cell_was_solved(cell)

        # Tell them more cells to solve (if any)
        return cells_to_solve



    def is_solved(self) :
        ''' returns true if board is solved '''
        return self.num_unsolved() == 0

    def num_unsolved(self) :
        ''' returns the number of unsolved cells.
        '''
        return len(self.unsolved_cells)


    def num_solved(self) :
        ''' returns the number of solved cells.
        '''
        return NUM_CELLS - self.num_unsolved()



    def output(self) :
        ''' returns list of rows of the Board.
        Same format as __init__ argument '''

        # Build [] of rows where every row is [] of cells in it
        list_of_rows = [[ cell.value for cell in self.rows[row_indx]] for row_indx in range(RCB_SIZE) ]

        return list_of_rows

    def __str__(self) :
        ''' returns human readable terse picture of a sudoku.
        The last line is terminated by a new line.

        Example:
         3 4 6  1 2 7  9 5 8
         7 8 5  6 9 4  1 3 2
         2 1 9  3 8 5  4 6 7

         4 6 2  5 3 1  8 7 9
         9 3 1  2 7 8  6 4 5
         8 5 7  9 4 6  2 1 3

         5 9 8  4 1 3  7 2 6
         6 2 4  7 5 9  3 8 1
         1 7 3  8 6 2  5 9 4

        '''
        ret_str = ""
        for row in self.rows :
            # row separator?
            if row.rcb_num and not row.rcb_num % BLK_SIZE :
                ret_str += '\n'
                
            # Print the cell values
            for cell in row :
                # Vertial block separator?
                if cell.col_num and not cell.col_num % BLK_SIZE :
                    ret_str += ' '

                # Cell's value
                ret_str += "%2d" % cell.value

            ret_str += '\n'

        return ret_str

    def str_unsolved_rcbs(self) :
        ''' returns printable information about
        all RCBs that aren't completely solved.
        '''
        ret_str = "" # What we return

        # Iterate over all unsolved rcbs
        for rcb in self.rcbs :
            if len(rcb.unsolved_cells) :
                # It's unsolved
                ret_str += str(rcb)
        return ret_str

    def _unique_board_name(self) :
        ''' Picks a unique name for the board comprised of:
        board-<current_time as bunch of numbers>
        '''
        nanosecs_from_1970 = time.time() * 10**9

        return "board-" + str(int(nanosecs_from_1970))

    def is_subset_of(self, their_board) :
        ''' returns True if every cell in our Board has
        the same value "their_board"
        '''
        # Iterate over both our cells
        for (our_cell, their_cell) in zip(self.cells, their_board.cells) :
            # Is our cell solved?
            if our_cell.value != Cell.unsolved_cell_value :
                # Yes, is it the same?
                if our_cell.value != their_cell.value :
                    return False # nope, they differ

        # If we fall out of the loop.. it's a subset
        return True
                

    # Operators
    def __eq__(self, their) :
        ''' == tester.  We just require all cells to have the same value
        and some possible_values
        '''
        # If they aren't a Board, we aren't equal
        if not isinstance (their, Board)  :
            return False

        # Iterate cells together
        for (our_cell, their_cell) in zip(self.cells, their.cells) :
            if our_cell.value != their_cell.value :
                return False  # we are NOT equal
            if our_cell.possible_values != their_cell.possible_values :
                return False

        # If we fall out, all cells matched.
        return True

    def sanity_check(self) :
        ''' Runs a variety of checks on the data structures.
        assert's on first failure.
        '''

        # Make sure all rows/cols/blks got populated
        for rcb_num in range(RCB_SIZE) :
            for indx in range(RCB_SIZE) :
                if not self.rows[rcb_num][indx] : assert "Unpopulated row:% entry:%d" % (rcb_num, indx)
                if not self.cols[rcb_num][indx] : assert "Unpopulated col:% entry:%d" % (rcb_num, indx)
                if not self.blks[rcb_num][indx] : assert "Unpopulated blk:% entry:%d" % (rcb_num, indx)

        # Make sure cells/rows/cols/blks all refer to the same cell
        # Raster scan cells/rows/cols/blks
        cell_num = 0
        for row_num in range(RCB_SIZE) :
            for col_num in range(RCB_SIZE) :

                # cells[] are in raster order
                cell = self.cells[cell_num]

                # Confirm cell number matches
                assert cell.cell_num == cell_num, "Cell.num %d should be %d" % (cell.cell_num, cell_num)

                # Confirm raster order
                assert cell.row_num == row_num, "cell%d has row#%d, should be %d" % (cell.cell_num,
                                                                                     cell.row_num, row_num)
                assert cell.col_num == col_num, "cell%d has col#%d, should be %d"  % (cell.cell_num,
                                                                                      cell.col_num, col_num)
                # We don't check blk because too hard to compute block number here.

                # The cells notion of row/col/blk should match ours
                assert cell.row is self.rows[cell.row_num], "Cell.row is wrong"
                assert cell.col is self.cols[cell.col_num], "Cell.col is wrong"
                assert cell.blk is self.blks[cell.blk_num], "Cell.blk is wrong"

                # We compare each row/col/blk to this cell
                cell_by_rows  = cell.row[cell.row_idx]
                cell_by_cols  = cell.col[cell.col_idx]
                cell_by_blks  = cell.blk[cell.blk_idx]

                # They should all be the same
                assert cell_by_rows is cell, "Cell#%d is not same as cell in rows[%d][%d]" % (cell_num,
                                                                                              cell.row_num,
                                                                                              cell.row_idx)
                assert cell_by_cols is cell, "Cell#%d is not same as cell in cols[%d][%d]" % (cell_num,
                                                                                              cell.col_num,
                                                                                              cell.col_idx)
                assert cell_by_blks is cell, "Cell#%d is not same as cell in blks[%d][%d]" % (cell_num,
                                                                                              cell.blk_num,
                                                                                              cell.blk_idx)
                # Advance to next cell
                cell_num += 1

        # If all out of loop... all went well
        return (True, None )

# Test code
import unittest
import copy
import itertools

class Test_board(unittest.TestCase):
    # Some CLASS-WIDE board specifications
    partial_spec_lrl = \
          [[0, 4, 6, 1, 2, 7, 9, 5, 8], 
           [7, 0, 5, 6, 9, 4, 1, 3, 2], 
           [2, 1, 9, 3, 8, 5, 4, 6, 7], 
           [4, 6, 2, 5, 3, 1, 8, 7, 9], 
           [9, 3, 1, 2, 7, 8, 6, 4, 5], 
           [8, 5, 7, 9, 4, 6, 2, 1, 3], 
           [5, 9, 8, 4, 1, 3, 7, 2, 6],
           [6, 2, 4, 7, 5, 9, 3, 8, 1],
           [1, 7, 3, 8, 6, 2, 5, 9, 4]]


    partial_spec_str = '''
           0 4 6 1 2 7 9 5 8 
           7 0 5 6 9 4 1 3 2 
           2 1 9 3 8 5 4 6 7 
           4 6 2 5 3 1 8 7 9 
           9 3 1 2 7 8 6 4 5 
           8 5 7 9 4 6 2 1 3 
           5 9 8 4 1 3 7 2 6
           6 2 4 7 5 9 3 8 1
           1 7 3 8 6 2 5 9 4
    '''

    partial_1_spec_str = '''
           3 0 6 1 2 7 9 5 8 
           7 0 0 6 9 4 1 3 2 
           2 1 9 3 8 5 4 6 7 
           4 6 2 5 3 1 8 7 9 
           9 3 1 2 7 8 6 4 5 
           0 0 0 9 0 6 2 1 3 
           5 9 8 4 1 3 7 2 6
           6 2 4 7 5 9 3 8 1
           1 7 3 8 6 2 5 9 0
    '''


    full_spec_lrl = [
        [3, 4, 6, 1, 2, 7, 9, 5, 8], 
        [7, 8, 5, 6, 9, 4, 1, 3, 2], 
        [2, 1, 9, 3, 8, 5, 4, 6, 7], 
        [4, 6, 2, 5, 3, 1, 8, 7, 9], 
        [9, 3, 1, 2, 7, 8, 6, 4, 5], 
        [8, 5, 7, 9, 4, 6, 2, 1, 3], 
        [5, 9, 8, 4, 1, 3, 7, 2, 6],
        [6, 2, 4, 7, 5, 9, 3, 8, 1],
        [1, 7, 3, 8, 6, 2, 5, 9, 4]
    ]
    

    def test_empty_board(self) :
        board = Board() # No cells should be solved

        # Confirm none solved
        for cell in board.cells :
            self.assertEqual (cell.value, Cell.unsolved_cell_value,
                         "Cell# %d should be unsolved, it is: %d" % (cell.cell_num, cell.value))
            # All values should be possible
            self.assertSetEqual (cell.possible_values, Cell.all_cell_values,
                                 "Cell# %d: num_possibles should have all possible values" %cell.cell_num)
                       
    def test_board_name(self) :
        name = "I never know what to call you"
        board = Board(None, name)
        self.assertEqual(name, board.name)
        self.assertEqual(board.description, "")  # No description supplied, default ""

        name = "The world is a tough place"
        desc = "Isn't that cynical?"
        board = Board(None, name, desc)
        self.assertEqual(name, board.name)
        self.assertEqual(board.description, desc)

    def test_unique_board_names(self) :

        # Generate a bunch of boards and make sure names are all different
        names_so_far = set()
        for cnt in range(100) :
            board = Board()

            assert board.name not in names_so_far

            names_so_far.add(board.name)
        

    def test_str_constructor(self) :
        ''' Make sure string and list of row-list generate same board '''
        lrl_spec = self.partial_spec_lrl
        str_spec = self.partial_spec_str
        self.assertEqual( Board(lrl_spec), Board(str_spec),
                          "string and list of row-lists generate different Boards")

    def test_copy_constructor(self) :

        # Make a couple of copies and insure they copy properly
        # and empty board
        in_board = Board() # empty
        out_board = Board(in_board)
        self.assertEqual(in_board, out_board)

        # random filled in board
        in_board = Board(self.partial_spec_str)
        out_board = Board(in_board)

        self.assertEqual(in_board, out_board) # produces same board
        self.assertEqual(out_board.name, in_board.name + "-cp.1")
        self.assertEqual(in_board.description, out_board.description)

        # copy # is correct
        # We have already made 1 copy
        for copy_cnt in range(2, 10) :
            out_board = Board(in_board)
            self.assertEqual (out_board.name, in_board.name + "-cp." + str(copy_cnt))

        # Make sure a specified name overrides picking from copied board
        speced_name = "We picked it"
        out_board = Board(in_board, speced_name)
        self.assertEqual( out_board.name, speced_name )
        self.assertEqual( out_board.description,
                          in_board.description)
        
        # Make sure a specified description overrides picking from copied board
        speced_desc = "Just for unittesting!"
        out_board = Board(in_board, None, speced_desc)
        self.assertEqual( out_board.description, speced_desc )


    def test_subset(self) :
        # What we test with
        some_board_spec = self.full_spec_lrl
        some_board = Board(some_board_spec, "some_board" )

        # An empty board is a subset of everything
        empty_board=Board()
        self.assertTrue ( empty_board.is_subset_of(some_board))

        # Everyboard is a subset of itself
        self.assertTrue (some_board.is_subset_of(some_board))

        # Create a legal subset by zeroing some elements
        subset_spec = copy.deepcopy(some_board_spec)
        subset_spec[0][3] = 0
        subset_spec[5][0] = 0
        subset_spec[2][3] = 0
        subset_spec[8][1] = 0
        subset_spec[4][0] = 0
        subset_board=Board(subset_spec, "subset_board", "For unit testing")
        self.assertTrue (subset_board.is_subset_of(some_board))        

        # Create a non-subset 
        non_subset_spec = [ [0]*9, [0]*9, [0]*9,
                            [0]*9, [0]*9, [0]*9,
                            [0]*9, [0]*9,
                            [0]*8 + [9]      # was a 4 in some_board
        ]

        non_subset_board=Board(non_subset_spec, "non subset board")
        self.assertFalse ( non_subset_board.is_subset_of(some_board) )

    def test_str_to_row_lists_errors(self) :

        # Number of values expected
        board_size = RCB_SIZE * RCB_SIZE
        board = Board() # empty board

        too_few_spec = '0' * (board_size-1)
        self.assertRaises(ExcBadStrToConvert, str_to_list_of_rows,too_few_spec)

        # Test too many digits in str
        too_many_spec = '0' * (board_size+1)
        self.assertRaises(ExcBadStrToConvert, str_to_list_of_rows, too_many_spec)

    def test_solve_stats(self) :

        # Can't really validate the solve stats
        # Just make sure it exists

        # unsolvable (empty board)
        board = Board() 
        self.assertIsNone   ( board.solve_stats.solve_time_secs )
        board.solve()
        self.assertIsNotNone( board.solve_stats.solve_time_secs )        

        # solvable
        board_spec = self.full_spec_lrl  # fully populated

        board = Board(board_spec) 
        self.assertIsNone   ( board.solve_stats.solve_time_secs )
        board.solve()
        self.assertIsNotNone( board.solve_stats.solve_time_secs )        

        

    def test_cell_all_neighbors(self) :
        # By rights it should be in the unittest for cell.py
        # but it can't because it would mean cyclical imports
        # so... we test it here

        board = Board()

        # Test a few at random
        cell = board[3][7]
        cell_neighbors_are = cell.all_neighbors()

        cell_neighbors_should_be  = [board.cells[idx] for idx in range(27, 36   ) if idx != cell.cell_num] # row
        cell_neighbors_should_be += [board.cells[idx] for idx in range( 7, 80, 9) if idx != cell.cell_num] # col
        cell_neighbors_should_be += [board.cells[idx] for idx in [42, 44, 51, 53]] # blk: that aren't in row/col
        cell_neighbors_should_be = set( cell_neighbors_should_be)

        self.assertEqual( cell_neighbors_are, cell_neighbors_should_be)
                                     

        cell = board[2][4]
        cell_neighbors_are = cell.all_neighbors()

        cell_neighbors_should_be  = [board.cells[idx] for idx in range(18, 27   ) if idx != cell.cell_num] # row
        cell_neighbors_should_be += [board.cells[idx] for idx in range( 4, 81, 9) if idx != cell.cell_num] # col
        cell_neighbors_should_be += [board.cells[idx] for idx in [3,5,12,14]] # blk: that aren't in row/col
        cell_neighbors_should_be = set( cell_neighbors_should_be)

        self.assertEqual( cell_neighbors_are, cell_neighbors_should_be)

        
    def test_is_solved_and_cnt(self) :

        # empty board
        board = Board()
        self.assertFalse ( board.is_solved() )
        self.assertEqual ( board.num_unsolved(), RCB_SIZE * RCB_SIZE )

        # Full populated board
        input_spec = self.full_spec_lrl
        board = Board(input_spec)
        self.assertTrue ( board.is_solved() )
        self.assertEqual ( board.num_unsolved(), 0 )
        
        # Partially populated board
        input_spec = self.partial_1_spec_str
        board = Board(input_spec)
        self.assertFalse ( board.is_solved() )
        self.assertEqual ( board.num_unsolved(), 8 )


    def test___eq__(self) :
        # Make some boards
        empty_board=Board()
        board_a = Board(self.partial_spec_str)
        board_b = Board(self.partial_1_spec_str)
        all_boards = [empty_board, board_a, board_b]

        # Board always equals itself
        for board in all_boards :
            self.assertEqual(board, board)

        # None of these boards should equal each other
        for ( left_board, right_board) in itertools.combinations( all_boards, 2) :
            self.assertNotEqual( left_board, right_board)

        # Copied boards should match
        board_a_copy = Board(board_a)
        self.assertEqual (board_a, board_a_copy)

        # Now we mildly diddle one cell and verify not equal
        #          0 1 2 3 4 5 6 7 8
        # Row#2:   7 0 0 6 9 4 1 3 2 

        # Change a Cell value
        board_diddled = Board(board_b)
        board_diddled[2][1].value = 4
        self.assertNotEqual( board_a, board_diddled )

        # Change a Cell possible_values
        board_diddled = Board(board_b)
        board_diddled[2][2].possible_values = set([4,5])
        self.assertNotEqual( board_a, board_diddled )


    def test_common_cell_rcbs(self) :

        # Former note:
        #     we are testing Cell.common_rcbs() which can't
        #     be testing in cell.py because it doesn't know
        #     about Boards to avoid a circular import loop
        # Well... that isn't true any more.  It is now
        # tested in Test_cell, but it doesn't hurt to test it again

        board=Board()

        base_cell         = board[4][5]
        cell_same_row     = board[4][6]
        cell_same_col     = board[2][5]
        cell_same_blk     = board[3][3]
        cell_with_none    = board[8][8]
        cell_same_row_blk = board[4][4]
        cell_same_col_blk = board[3][5]

        all_test_cells = [cell_same_row,
                          cell_same_col,
                          cell_same_blk,
                          cell_with_none
                          ]

        row_rcb = base_cell.row
        col_rcb = base_cell.col
        blk_rcb = base_cell.blk

        self.assertEqual( base_cell.common_rcbs( []               ), [] )
        self.assertEqual( base_cell.common_rcbs( [cell_with_none] ), [] )

        self.assertEqual( base_cell.common_rcbs( [cell_same_row]     ), [row_rcb] )
        self.assertEqual( base_cell.common_rcbs( [cell_same_col]     ), [col_rcb] )
        self.assertEqual( base_cell.common_rcbs( [cell_same_blk]     ), [blk_rcb] )

        self.assertEqual( base_cell.common_rcbs( [cell_same_row_blk] ), [row_rcb, blk_rcb] )
        self.assertEqual( base_cell.common_rcbs( [cell_same_col_blk] ), [col_rcb, blk_rcb] )

        self.assertEqual( base_cell.common_rcbs( all_test_cells ), [] )

    def test_input_bad_input_wrong_row_cnt(self) :
        # Only 7 rows, values don't matter
        puzzle = [ [0] * 9 for i in range(7) ]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Wrong number of rows: 7')

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(puzzle))


    def test_input_bad_value(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]
        
        # Make a single bad value
        puzzle[3][6] = 18

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message,
                             'Bad value: 18 at (row,col) (3,6)')

    def test_input_bad_input_wrong_row_size(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]

        # remove an cell from a row
        puzzle[4] = puzzle[4][1:]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Row 4: Wrong size: 8')

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(puzzle))


    def test_input_duplicate_values(self) :
        some_board_spec = [ \
                            [0, 4, 6, 1, 2, 7, 9, 5, 8], # 0 row
                            [7, 0, 0, 6, 9, 4, 1, 3, 2], # 1 row
                            [2, 1, 9, 0, 0, 0, 4, 6, 7], # 2 row
                            [4, 6, 2, 5, 3, 1, 0, 0, 0], # 3 row
                            [0, 3, 0, 2, 0, 8, 0, 0, 0], # 4 row
                            [8, 5, 7, 9, 4, 6, 2, 0, 3], # 5 row
                            [0, 9, 8, 4, 1, 3, 7, 2, 6], # 6 row
                            [6, 2, 4, 7, 5, 9, 3, 8, 1], # 7 row
                            [1, 7, 3, 8, 6, 2, 5, 9, 4]  # 8 row
                #       col  0  1  2  3  4  5  6  7  8
        ]

        # Make some illegal input
        # duplicate value in a row
        dup_in_row = copy.deepcopy(some_board_spec)
        dup_in_row[3][7] = 1
        expected_err_msg = "cell#34 at (3,7) value:1 is duplicated in cell's row"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_row) # Make sure it raise the exception
        try:
            board = Board(dup_in_row)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(dup_in_row))



        # duplicate value in a col
        dup_in_col = copy.deepcopy(some_board_spec)
        dup_in_col[4][7] = 5
        dup_in_col[3][3] = 0 # avoid duplicate in the block
        expected_err_msg = "cell#43 at (4,7) value:5 is duplicated in cell's col"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_col) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_col)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(dup_in_col))


        # duplicate value in a blk
        dup_in_blk = copy.deepcopy(some_board_spec)
        dup_in_blk[6][7] = 4
        expected_err_msg = "cell#61 at (6,7) value:4 is duplicated in cell's row"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_blk) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_blk)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(dup_in_blk))

    def test_solve_cells(self) :
        # Empty Board
        board = Board()

        # Solve 1 cell only
        # Shouldn't solve any others
        cells_to_solve = set( [CellToSolve( board[4][6], 3)])
        num_solved = board.solve_cells( cells_to_solve)
        self.assertEqual( num_solved, 1)
        self.assertEqual( len( board.unsolved_cells), NUM_CELLS-1)


        # Board with 4 unsolved that don't influence each other
        input_spec ='''
         0 4 6 1 2 7 9 5 8 
         7 8 5 6 9 4 1 3 0 
         2 1 9 3 8 5 4 6 7 
         4 0 2 5 3 1 8 7 9 
         9 3 1 2 7 8 6 0 5 
         8 5 7 9 4 6 2 1 3 
         5 9 8 4 1 3 7 2 6
         6 2 4 7 5 9 3 8 1
         1 7 3 8 6 2 5 9 4
        '''
        board = Board(input_spec)
        solutions = [ CellToSolve( board[0][0] , 3 ),
                      CellToSolve( board[1][8] , 2 ),
                      CellToSolve( board[3][1] , 6 ),
                      CellToSolve( board[4][7] , 4 )
                      ]
        # Make sure we got that right
        for (cell,value) in solutions :
            self.assertTrue (cell in board.unsolved_cells)
            self.assertTrue (value in cell.possible_values)

        # Solve each cell in turn and make sure they solve the right amt of others
        for cell_to_solve in solutions :
            num_solved = board.solve_cells( set([ cell_to_solve ]))
            self.assertEqual( num_solved, 1)
        self.assertTrue ( board.is_solved() )

            
        # Partially populated board
        input_spec ='''
         3 0 6 1 2 7 9 5 8 
         7 0 0 6 9 4 1 3 2 
         2 1 9 3 8 5 4 6 7 
         4 6 2 5 3 1 8 7 9 
         9 3 1 2 7 8 6 4 5 
         0 0 0 9 0 6 2 1 3 
         5 9 8 4 1 3 7 2 6
         6 2 4 7 5 9 3 8 1
         1 7 3 8 6 2 5 9 0
        '''

        board = Board(input_spec)

        # All the cells that will solve this
        solutions = [ CellToSolve( board[0][1] , 4 ),
                      CellToSolve( board[1][1] , 8 ),
                      CellToSolve( board[1][2] , 5 ),
                      CellToSolve( board[5][0] , 8 ),
                      CellToSolve( board[5][1] , 5 ),
                      CellToSolve( board[5][2] , 7 ),
                      CellToSolve( board[5][4] , 4 ),
                      CellToSolve( board[8][8] , 4 )
                      ]
        # Make sure we got that right
        self.assertEqual (len(solutions), len(board.unsolved_cells))
        for (cell,value) in solutions :
            self.assertTrue (cell in board.unsolved_cells)

            
        # Now solve it
        num_solved = board.solve_cells ( solutions )
        self.assertEqual ( num_solved, len( solutions) )
        self.assertTrue  ( board.is_solved() )


    def test_common_rcbs(self) :

        # empty board
        board = Board()

        #### Cells with no rcbs in common
        ncc = [\
               board[0][0],
               board[1][3],
               board[2][6],
               board[3][1],
               board[4][4],
               board[5][7],
               board[6][2],
               board[7][5],
               board[8][8],
               ]
        for cell in ncc :
            # One at a time, test against all others
            common_rcbs = cell.common_rcbs( [ other_cell for other_cell in ncc if cell != other_cell])
            self.assertFalse (common_rcbs) 


        #### Row and blk in common
        cell_a = board[6][7]
        cell_b = board[6][6]
        self.assertEqual   ( cell_a.row_num,  cell_b.row_num )
        self.assertEqual   ( cell_a.blk_num,  cell_b.blk_num )
        self.assertNotEqual( cell_a.col_num,  cell_b.col_num )

        ones_in_common = cell_a.common_rcbs( [cell_b] )
        self.assertEqual ( len(ones_in_common), 2)
        self.assertTrue  ( board.rows[6] in ones_in_common )
        self.assertTrue  ( board.blks[8] in ones_in_common )

        ### col and blk in common
        cell_a = board[4][7]
        cell_b = board[5][7]
        self.assertNotEqual( cell_a.row_num,  cell_b.row_num )
        self.assertEqual   ( cell_a.blk_num,  cell_b.blk_num )
        self.assertEqual   ( cell_a.col_num,  cell_b.col_num )

        ones_in_common = cell_a.common_rcbs( [cell_b] )
        self.assertEqual ( len(ones_in_common), 2)
        self.assertTrue  ( board.blks[5] in ones_in_common )
        self.assertTrue  ( board.cols[7] in ones_in_common )

        
    def test_most_constrained_cell_num(self) :
        # None solved, should return cell#0
        bd = Board()
        self.assertEqual(0, bd.most_constrained_cell_num() )

        # All solved,  should return cell#0
        bd = Board(Test_board.full_spec_lrl)
        self.assertEqual(0, bd.most_constrained_cell_num() )
    

        # One unsolved cell.  It should be returned
        lrl = copy.deepcopy(Test_board.full_spec_lrl)
        lrl[4][8] = 0
        bd = Board(lrl)
        self.assertEqual(4*9 + 8, bd.most_constrained_cell_num() )

        # Two unsolved cells with same rcb unsolved count
        # Should pick the first (by cell #)
        lrl = copy.deepcopy(Test_board.full_spec_lrl)
        lrl[3][7] = 0
        lrl[6][2] = 0
        bd = Board(lrl)
        self.assertEqual(3*9 + 7, bd.most_constrained_cell_num() )
        

        # Three unsolved cells with different rcb unsolved count
        lrl = copy.deepcopy(Test_board.full_spec_lrl)
        lrl[4][2] = 0 # same blk
        lrl[5][1] = 0 # same blk
        lrl[2][4] = 0 # should pick this one
        bd = Board(lrl)
        self.assertEqual(2*9 + 4, bd.most_constrained_cell_num() )
        

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    

