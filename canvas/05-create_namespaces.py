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
    # course = cs123, course_no = 123
    course_no = re.split('(\d+)', course)[1]
    
    br_name = "br" + course_no # br123
    br_ip = "10.0." + course_no + ".1/24" # 10.0.123.1/24
    filename = f"/etc/systemd/system/netns/bridge-{course_no}.conf"
    conf = f"BR_IP={br_ip}"
    with open(filename, 'w') as fout:
        fout.write(conf)
    
    instance = f"netbr@{course_no}.service"

    p = subprocess.run(["systemctl", "start", instance], stdout=PIPE)
    if p.returncode == 0:
        logger.info("Bridge " + br_name + " created for " + course + ", ip=" + br_ip)
    else:
        logger.info("Error creating bridge for " + course)

    return [course_no, br_name, br_ip]


# create network namespace configuration files used by systemd
def create_ns_config(br, usernames):
    course_no = str(br[0])
    br_name = br[1]
    brgw_ip = br[2].rsplit('/', 1)[0]
    subnet = brgw_ip.rsplit('.', 1)[0]
    netmask = "/24"    
    num = 10
    
    namespaces = []
    for u in usernames: 
        ns = course_no + str(num) # 12310
        ns_name = "ns" + ns # ns12310
        vr_ip = subnet + "." + str(num) + netmask
        filename = f"/etc/systemd/system/netns/{ns_name}.conf"
        conf = f"VR_IP={vr_ip}\nBR={br_name}\nBR_IP={brgw_ip}"
        with open(filename, 'w') as fout:
            fout.write(conf)
        namespace = u + ":" + ns_name + ":" + vr_ip # cs123-newellz2:ns12310:10.0.123.10
        namespaces.append(namespace)
        num += 1
    
    return namespaces
        

# start service to test network configuration in namespaces
def create_netns(namespaces):

    for n in namespaces: 
        # cs123-newellz2:ns12310:10.0.123.10
        namespace = n.split(':')
        user = namespace[0]
        ns_name = namespace[1]
        ns = re.split('(\d+)', ns_name)[1] 
        vr_ip = namespace[2]

        instance = f"testnetns@{ns}.service"
        
        p = subprocess.run(["systemctl", "start", instance], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Network namespace " + ns_name + " created for " + user + ", ip=" + vr_ip)
        else:
            logger.info("Error creating namespace for " + user)


def main():
    with open(args.passwd_list.name) as fin:
        usernames = [line.split(':')[0] for line in fin]

    course = usernames[0].split("-")[0]
    
    br = create_br(course)
    
    ns = create_ns_config(br, usernames)

    create_netns(ns)
    
    # create file with list of ns_name:ip for each user
    filename = course + "/" + course + "-netns.txt"
    with open(filename, 'w') as fout:
        fout.write("\n".join(n for n in ns))
    
    print(f"\n\t file created: {filename} \n")


if __name__ == "__main__":
    main()
