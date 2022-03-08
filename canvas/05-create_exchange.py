#!/usr/bin/env python3

# Creates exchange directory for Jupyter extension nbgrader
# ./create_exchange.py CS123/CS123-netids.txt
# (run get_course_enrollments.py to generate list file)

import sys # for sys.exit, sys.argv
import logging 
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help
import os # mkdirs to recursively create directories
import subprocess
from subprocess import PIPE

# setup CLI args and help
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Create exchange directory for nbgrader
        '''),
        epilog=textwrap.dedent('''\
        '''))

parser.add_argument('netid_list', type=argparse.FileType('r'), 
                    help='Text file, COURSE in header. Run get_course_enrollments to generate.')
args = parser.parse_args()

# setup logging:
LOG_FILE= ''
FORMAT = ''
logging.basicConfig(level=logging.INFO,
                     format = FORMAT)

#CONSOLE LOGGING
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)

#INFO LOGGER
logger = logging.getLogger('dev')
logger.setLevel(logging.INFO)
logger.addHandler(consoleHandler)
# to prevent doubling of error messages in output:
logger.propagate = False


def main():

    with open(args.netid_list.name) as fin: 
        header = fin.readline()

    course = header.split(':')[0]

    exchange = course + "/exchange"

    # see https://nbgrader.readthedocs.io/en/stable/user_guide/managing_assignment_files.html#
    # can change to manual implmentation to use CMS: 
    # https://nbgrader.readthedocs.io/en/stable/user_guide/managing_assignment_files_manually.html
    if not os.path.exists(exchange):
        #os.makedirs(exchange, mode=777) # mode ignored, must call chmod explicitly
        os.makedirs(exchange)

    p = subprocess.run(["chmod", "777", exchange], stdout=PIPE)
    if p.returncode == 0:
        logger.info("\n\t Exhange directory created for " + course + " at " + exchange + "\n")
    else:
        logger.info("Error creating exhange directory for " + course)


    sys.exit(0)


if __name__ == "__main__":
    main()

