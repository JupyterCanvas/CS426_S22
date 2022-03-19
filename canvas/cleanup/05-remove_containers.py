#!/usr/bin/env python3

# Remove user containers from list of usernames
# ./cleanup/remove_containers.py CS123/CS123-pass.txt
# (run add_users.py to generate username list file)

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
        Remove containers created with create_containers.py
        '''),
        epilog='\
        ')

parser.add_argument('passwd_list', type=argparse.FileType('r'), 
                    help='List of usernames in a text file \
                    run add_users.py to generate cs123/cs123-pass.txt')
            
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

def stop_instances(usernames):
    
    for user in usernames: 
        instance = f"cont@{user}.service"
        p = subprocess.run(["systemctl", "stop", instance], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Container " + instance + " stopped")
        else:
            logger.info("Error stopping container " + instance)

def main():
    with open(args.passwd_list.name) as fin:
        usernames = [line.split(':')[0] for line in fin]

    stop_instances(usernames)

if __name__ == "__main__":
    main()
