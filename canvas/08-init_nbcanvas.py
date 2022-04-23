#!/usr/bin/env python3

# Start websockify instances for users on server
# ./start_websockify.py CS123/CS123-urls.txt
# (run create_urls.py to generate url list file)

import sys # for sys.exit, sys.argv
import logging 
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help
import subprocess
from subprocess import PIPE
import re # for regular expression matching 

# setup CLI args and help
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        '''),
        epilog='\
        ')

parser.add_argument('instance_list', type=argparse.FileType('r'),
                    help='List of container instances in a text file \
                    run create_containers.py to generate cs123/cs123-conts.txt')

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

def init_nbcanvas(instances): 
    for i in instances: 
        user = i.split(':')[0]
        
        instance = f"nbcanvas@{user}.service"
        
        p = subprocess.run(["systemctl", "start", instance], stdout=PIPE)
        if p.returncode == 0: 
            logger.info("nbcanvas initialized for " + user)
        else: 
            logger.info("Error initializing nbcanvas for " + user)


def main():
    with open(args.instance_list.name) as fin:
        instances = [inst.strip() for inst in fin]

    init_nbcanvas(instances)


if __name__ == "__main__":
    main()
