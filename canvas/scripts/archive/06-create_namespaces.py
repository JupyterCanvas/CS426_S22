#!/usr/bin/env python3

# Creates network namespaces for user containers
# ./create_namespaces.py CS123/CS123-pass.txt
# (run add_users.py to generate list file)

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
        Create network namespaces for user containers
        '''),
        epilog=textwrap.dedent('''\
        To enable ip forwarding and nat for network access in container
        server should have the following set: 
        (this is ephemeral, should change to persistent/load at boot)
        
            sysctl -w net.ipv4.ip_forward=1
            iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE

        check with: 
            sysctl net.ipv4.ip_forward
            iptables -L -t nat -v -n

        '''))

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


def create_br(course):
    br_name = "br-" + course
    course_no = re.split('(\d+)', course)[1]
    br_ip = "10.0." + course_no + ".1/24"

    # create bridge and assign ip 
    # $1 = br_name, $2 = br_ip
    p = subprocess.run(["./scripts/create-course-br.sh", br_name, br_ip], stdout=PIPE)
    if p.returncode == 0:
        logger.info("Bridge " + br_name + " created for " + course + ", ip=" + br_ip)
    else:
        logger.info("Error creating bridge for " + course)

    return [br_name, br_ip, course_no]

def create_ns(br, usernames, course):
    br_name = br[0]
    br_ip = br[1].rsplit('/', 1)[0]
    course_no = br[2]
    subnet = br_ip.rsplit('.', 1)[0] 
    netmask = "/24"
    num = 10

    namespaces = []
    for u in usernames: 
        ns_name = "ns-" + u
        veth_l = "vl-" + str(course_no) + "-" + str(num)
        veth_r = "vr-" + str(course_no) + "-" + str(num)
        veth_r_ip = subnet + "." + str(num) + netmask
        p = subprocess.run(["./scripts/create-user-ns.sh", ns_name, veth_l, veth_r, veth_r_ip, br_name, br_ip], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Namespace " + ns_name + " created with ip: " + veth_r_ip)
            ns = ns_name + ":" + veth_r_ip
            namespaces.append(ns)
            num += 1 # increment ip for next user
        else:
            logger.info("Error creating namespace for " + u)
            sys.exit(0)

    # create file with list of ns_name:ip for each user
    filename = course + "/" + course + "-netns.txt"
    with open(filename, 'w') as fout:
        fout.write("\n".join(n for n in namespaces))

    print(f"\n\t file created: {filename} \n")
            
def main():
    with open(args.passwd_list.name) as fin:
        usernames = [line.split(':')[0] for line in fin]

    course = usernames[0].split("-")[0]

    br = create_br(course)
    
    create_ns(br, usernames, course)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

