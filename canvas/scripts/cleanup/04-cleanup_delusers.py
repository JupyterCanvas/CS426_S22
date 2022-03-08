#!/usr/bin/env python3

# remove users from server with list of netids
# ./cleanup_delusers.py CS123/CS123-netids.txt
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
        Delete users from server from list of netids
          (run get_course_enrollments.py to generate list file)
          removes user account, user group, user home
          for future implementation, need to not remove
          subuid and subgid mapping but deactivate instead. 
        '''),
        epilog=textwrap.dedent('''\
        '''))

parser.add_argument('netid_list', type=argparse.FileType('r'),
                    help='List of user netids in a text file')

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

def del_user(usernames):
    for u in usernames:
        p = subprocess.run(["deluser", "--remove-home", u], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Removed user: " + u)
        else: 
            logger.info("Error removing user: " + u)

def main():

    with open(args.netid_list.name) as fin: 
        lines = [line.strip() for line in fin]
    
    header = lines[0]
    course = header.split(':')[0]

    # skip header and comments
    netids = [n for n in lines[1:] if not n.startswith('#')]
    
    usernames = []
    for netid in netids: 
        username = course + "-" + netid
        usernames.append(username)

    del_user(usernames)

    sys.exit(0)


if __name__ == "__main__":
    main()

