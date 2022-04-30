#!/usr/bin/env python3
#<filename> [filename] <fixme>
#<path>  [path] <fixme>
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
    <fixme>
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

    # Common optional arguments <fixme>
    parser.add_argument("-v", "--verbose",
                        help="Print all changed filenames.",
                        action="store_true")

    parser.add_argument("-d", "--dry_run",
                        help="Nothing changed, only print what would be done.",
                        action="store_true")

    args = parser.parse_args()

    #<fixme> Code goes here

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


