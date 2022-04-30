#!/usr/bin/env python3
# diddle.py
#<filename> [filename] <fixme>
#<path>  [path] <fixme>
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
Usage: diddle.py [-r,--replace] filename line_num

Puts/inserts 20 lines of random text in filename @line_num
If --replace, replaces those lines otherwise inserts them

'''
#<\mod_doc>

#<copyright> Copyright (c) 2020 Dinkum Software
#<lic>
'''Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
''' #</lic>

#<authors> tc    tom campbell, www.DinkumSoftware.com <todo> change to .org

#<history>
#    2020-10-02 tc Initial
#    2020-12-19 tc Added argparse and append ERROR: to main returns
#</history>

import sys
import argparse
import textwrap    # dedent

from datetime import *

def random_line() :
    
    return "#diddle: xyzzy %s\n" % datetime.now().strftime("%a %f")

def main() :
    ''' See module doc

    Normally returns NONE
    On error, returns a printable description of the error
    '''

    # Specify and parse the command line arguments
    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__)
    )

    parser.add_argument("filename") ;
    parser.add_argument("line_num") ;

    # Common optional arguments <fixme>
    parser.add_argument("-r", "--replace",
                        help="replace the lines",
                        action="store_true")

    args = parser.parse_args()

    num_lines_to_diddle = 10
    start_line = int(args.line_num)
    end_line   = start_line + num_lines_to_diddle

    with open( args.filename, 'r' ) as f :
        lines = f.readlines()
    print ( len(lines) )

    if args.replace :
        for lnum in range(start_line, end_line) :
            lines[lnum] = ""


    for lnum in range(start_line, end_line) :
        lines[lnum] = random_line()

    with open (args.filename, 'w') as f :
        for l in lines :
            f.write(l) ;

# main() launcher
if __name__ == '__main__':
    try:
        # This handles normal and error returns
        err_msg = main()    # returns human readable str on error
        if err_msg :
            err_msg = "ERROR:" + err_msg  # Label the output
        sys.exit( err_msg )

    except KeyboardInterrupt as e:
        # Ctrl-C
        sys.exit( "KeyboardInterrupt: Probably Control-C typed.")

    except SystemExit as e: # sys.exit()
        # Just pass it along
        raise e

    # Let any other Exception run it's course

    assert False, "Can't get here"


