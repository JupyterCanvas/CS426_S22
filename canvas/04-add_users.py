#!/usr/bin/env python3

# Adds users to server from list of netids
# ./add_users.py CS123/CS123-netids.txt
# (run get_course_enrollments.py to generate list file)

import re # for regular expression matching (in pagination)
import sys # for sys.exit, sys.argv
import pprint # pretty print python data structures
import logging 
import requests # to send HTTP requests with Python
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help
import os # mkdirs to recursively create directories

# setup CLI args and help
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Add users to server from list of netids
          (run get_course_enrollments.py to generate list file)
          Generates: 
            user accounts on server per course 
            user subuid/subgid mapping for container fakeroot
            user home directories
        '''),
        epilog=textwrap.dedent('''\
        To prevent accidental clobbering between course containers, 
        usernames are netids prepended with the course: cs123-sskidmore
        '''))

parser.add_argument('netid_list', type=argparse.FileType('r'), 
                    help='List of user netids in a text file \
                    Run get_enrollments.py to generate')
args = parser.parse_args()

# setup logging:
LOG_FILE= ''
FORMAT = ''
logging.basicConfig(level=logging.INFO,
                     format = FORMAT)
formatter = logging.Formatter(FORMAT)
logger = logging.getLogger("")
logger.handlers = []
logger_fh = logging.StreamHandler(sys.stdout)
logger_fh.setFormatter(formatter)
logger.addHandler(logger_fh)

def add_user(usernames):
    for u in usernames:
        print(u)

def set_temp_pass(usernames):
    for u in usernames: 
        print(u)
        r = requests.get('http://www.dinopass.com/password/strong')
        passwd = r.text
        print(passwd)

def main():

    with open(args.netid_list.name) as fin: 
        lines = [line.strip() for line in fin]

    header = lines[0]
    course = header.split(':')[0]

    netids = [n for n in lines[1:] if not n.startswith('#')]
    
    usernames = []
    for netid in netids: 
        username = course + "-" + netid
        usernames.append(username)

    add_user(usernames)

    set_temp_pass(usernames)

    sys.exit(0)


if __name__ == "__main__":
    main()

