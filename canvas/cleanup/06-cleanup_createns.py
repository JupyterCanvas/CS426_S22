#!/usr/bin/env python3

# Adds users to server from list of netids
# ./add_users.py CS123/CS123-netids.txt
# (run get_course_enrollments.py to generate list file)

import sys # for sys.exit, sys.argv
import logging 
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help
import subprocess
from subprocess import PIPE

# setup CLI args and help
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Remove network namespaces created with create_namespaces.py 
        '''),
        epilog=textwrap.dedent('''\
        '''))

parser.add_argument('netns_list', type=argparse.FileType('r'), 
                    help='List of network namespaces in a text file \
                    run create_namespaces.py to generate cs123/cs123-netns.txt')
            
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

    with open(args.netns_list.name) as fin:
        namespaces = [line.split(':')[0] for line in fin]
    course = namespaces[0].split("-")[1]
    br = "br-" + course

    p = subprocess.run(["ip", "link", "del", br], stdout=PIPE)
    if p.returncode == 0:
        logger.info("Bridge " + br + " removed")
    else:
        logger.info("Error removing bridge " + br)

    for ns in namespaces: 
        p = subprocess.run(["ip", "netns", "del", ns], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Namespace " + ns + " removed")
        else:
            logger.info("Error removing namespace " + ns)

    sys.exit(0)


if __name__ == "__main__":
    main()

