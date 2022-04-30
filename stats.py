#!/usr/bin/env python3
# dinkum/sudoku/stats.py
''' Defines class Stats which has various
statistics about solving a sudoku Board.
'''

# 2019-12-09 tc Initial
# 2020-02-24 tc Made comply with dinkum_python_run_unittests

class Stats :
    ''' Holds statistics about solving a
    sudoku Board:
        solve_start_time_secs  When solve() called
        solve_time_secs        How long Board.solve() ran

    Subtraction of two Stats is supported to compute
    the change in statistics
    '''

    def __init__(self) :
        ''' Constructs a Stats with all values set to None
        '''
        self.solve_start_time_secs = None # when solve() called
        self.solve_time_secs       = None # How long it ran
        self.num_solve_passes      = None # How many time the
                                          # solve() loop ran


    def __sub__(self, other) :
        ''' subtract two Stats.
        Each member of other is subtracted from corresponding
        member in self.

        Returns NotImplemented if other isn't a Stat
        '''
        if not isinstance(other, Stats) :
            return NotImplemented

        # What we return
        ret_class = Stats() # All members should be None


        # Do the subtraction
        # TypeError is typically from trying to subtract
        # a None entry, we just leave the returned value as None
        # which is set in the constructor.
        for (ret_member_name,
             self_member_value,
             other_member_value) in zip ( vars(ret_class),
                                          vars(self) .values(),
                                          vars(other).values())  :
            try :
                setattr(ret_class, ret_member_name,
                        self_member_value - other_member_value)
            except TypeError :
                pass
        
        # All done
        return ret_class


    def __str__(self) :
        ''' Return human readable member names and values.
        '''
        ret_str = "" # what we return

        for (name, value) in vars(self).items() :
            ret_str += "%s: %s\n" % (name, str(value))
        return ret_str


# Test code
import unittest

class Test_stats(unittest.TestCase):

    def test_construction(self) :
        s = Stats()

        # Check all the members
        for value in vars(s).values() :
            self.assertIsNone (value)

    def test_substraction(self) :
        # Subtracting class of all None's should produce the same
        results = Stats() - Stats()

        # Check all the members
        for value in vars(results).values() :
            self.assertIsNone( value )

        # Subtracting class from itself should produces 0's
        stat = Stats()
        stat.solve_start_time_secs = 5732222.83215
        stat.solve_time_secs       = 18.234
        stat.num_solve_passes      = 50
       
        results = stat - stat

        # Check all the members
        for value in vars(results).values() :
            if isinstance(value, float) :
                self.assertAlmostEqual( value, 0.0, 4)
            else :
                self.assertEqual( value, 0 )

        # Check a couple of members
        left  = Stats()
        right = Stats()

        left.solve_time_secs =   18.0
        right.solve_time_secs = - 5.0

        result = left - right
        self.assertAlmostEqual( result.solve_time_secs, 23.0, 4)
       
        # Make sure it doesn't try to subtract an unknown class
        with self.assertRaises(TypeError) as cm:
            class Foo () : pass
            x = Stats() - Foo()
        
        #  Make sure deals with None's correctly
        a_class = Stats() # All members None
        a_class.solve_time_secs = 18.4321

        b_class  = Stats() # Some set
        b_class.solve_start_time_secs = 4568322.4

        a_minus_b = a_class - b_class
        self.assertIsNone ( a_minus_b.solve_time_secs )
        self.assertIsNone ( a_minus_b.solve_start_time_secs )

        b_minus_a = b_class - a_class
        self.assertIsNone ( b_minus_a.solve_time_secs )
        self.assertIsNone ( b_minus_a.solve_start_time_secs )
        

    def test_str(self) :
        # Just make sure it runs
        s = str(Stats())

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
