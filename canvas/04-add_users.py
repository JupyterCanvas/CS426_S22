#!/usr/bin/env python3

# Adds users to server from list of netids
# ./add_users.py CS123/CS123-netids.txt
# (run get_course_enrollments.py to generate list file)

import sys # for sys.exit, sys.argv
import logging 
import requests # to send HTTP requests with Python
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help
import subprocess
from subprocess import PIPE

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
            temporary passwords that users must change at first login
            text file with list of usernames and OTPs: cs135/cs135-pass.txt
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

#CONSOLE LOGGING
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)

#INFO LOGGER
logger = logging.getLogger('dev')
logger.setLevel(logging.INFO)
logger.addHandler(consoleHandler)
# to prevent doubling of error messages in output:
logger.propagate = False

# creates user, home with skel, subuid/subgid, sets shell to bash
def add_user(usernames):
    for u in usernames:
        p = subprocess.run(["useradd", "--create-home", "--shell", "/bin/bash", u], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Added user: " + u)
        else: 
            logger.info("Error adding user: " + u)
        # add files to user home directories to test home bind in containers
        p2 = subprocess.run(["./createfiles.sh", u], stdout=PIPE)
        if p2.returncode == 0:
            logger.info("Added test files for user: " + u)
        else: 
            logger.info("Error adding test files for user: " + u)

# for development, need to update for production
def set_temp_pass(usernames):
    course = usernames[0].split("-")[0]
    
    strings = []
    
    # get temp passwords from dinopass generator
    for u in usernames: 
        r = requests.get('http://www.dinopass.com/password/strong')
        tpass = r.text
        # create string for chpasswd = user:passwd
        string = u + ":" + tpass
        strings.append(string)
    
    # create file to provide chpasswd will user strings
    with open('pass.txt', 'a') as fout: 
        fout.write("\n".join(s for s in strings))
    
    # can't set passwd through subprocess, running script instead:
    # setpass.sh = cat pass.txt | chpasswd
    p = subprocess.run(["./setpass.sh"], stdout=PIPE)
    if p.returncode == 0:
        logger.info("Added temporary user passwords for " + course)
    else: 
        logger.info("Error adding passwords for  " + course)
   
    # force user to change password at first login
    # after logging in with the temp password we provide, user will see: 
    # You are required to change your password immediately (administrator enforced).
    # Changing password for cs123-newellz2.
    # Current password:
    for u in usernames: 
        p = subprocess.run(["passwd", "-e", u])
        if p.returncode == 0:
            logger.info("User must change password at next login: " + u)
        else: 
            logger.info("Error setting password to expire for user: " + u)
    
    # move file from cwd to course dir
    filename = course + "/" + course + "-pass.txt"
    p = subprocess.run(["mv", "pass.txt", filename], stdout=PIPE)
    if p.returncode == 0:
        print(f"\n\t file created: {filename} \n")
    else:
        logger.info("Error moving pass.txt to course directory")


def main():

    with open(args.netid_list.name) as fin: 
        lines = [line.strip() for line in fin]

    header = lines[0]
    course = header.split(':')[0]

    # remove role lines i.e. "# insructors:" from list
    netids = [n for n in lines[1:] if not n.startswith('#')]
    
    usernames = []
    for netid in netids: 
        username = course + "-" + netid.split(':')[0]
        usernames.append(username)

    add_user(usernames)

    set_temp_pass(usernames)

    sys.exit(0)


if __name__ == "__main__":
    main()


