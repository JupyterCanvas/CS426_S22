#!/usr/bin/env python3

# Generate user containers from list of usernames
# ./create_containers.py CS123/CS123-pass.txt
# (run add_users.py to generate username list file)

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
        Create user containers from list of usernames:
          (run add_users.py to generate passwd_list)
          Generates:
            cni config for course subnet bridge
            user container config files
            user container instance services
            service to test networking config in user containers
            text file with list of usernames and container ips: cs135/cs135-conts.txt
        '''),
        epilog=textwrap.dedent('''\
        Run systemctl status testcont@username.service to check container networking 
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

# create cni config for course subnet bridge
def create_br_config(course):
    
    # this is not going to work for course #s > 255, 
    # need to update algorithm for assigning subnet 
    
    # also need to add check for existing subnet
    # check file (in containers/) before creating new subnet
    # print subnet to file (append)

    # course = cs123, course_no = 123
    course_no = re.split('(\d+)', course)[1]
    
    bridge = "br" + course_no # br123
    subnet = "10.0." + course_no + ".0/24" # 10.0.123.0/24

    # must be named fakeroot, can't have multiple files
    # create new config/clobber existing whenever creating new instances
    # to include a brace chars in literal text, escaped by doubling {{ = "{"
    config = f'''{{
    "cniVersion": "1.0.0",
    "name": "fakeroot",
    "plugins": [
        {{
            "type": "bridge",
            "bridge": "{bridge}",
            "isGateway": true,
            "ipMasq": true,
            "ipam": {{
                "type": "host-local",
                "subnet": "{subnet}",
                "routes": [
                    {{ "dst": "0.0.0.0/0" }}
                ]
            }}
        }},
        {{
            "type": "firewall"
        }},
        {{
            "type": "portmap",
            "capabilities": {{"portMappings": true}},
            "snat": true
        }}
    ]
}}
'''
    with open("/usr/local/etc/singularity/network/01_contbridge.conflist","w") as f:
        f.write(config)

    return(bridge, subnet)

# create container instance configuration files used by systemd
def create_inst_config(subnet, usernames):
    # split subnet into nework and host 
    # subnet = 10.0.123.0, network = 10.0.123
    network = subnet.rsplit('.', 1)[0]
    # first host address
    host = 10
    
    instances = []
    num = 1
    for user in usernames: 
        # generate instance config file for each user
        filename = f"/etc/systemd/system/containers/inst-{user}.conf"
        inst_ip = network + "." + str(host)
        conf = f'IP="IP={inst_ip}"\nVNCP={num}\n'
    
        with open(filename, 'w') as fout:
            fout.write(conf)

        # create list of user instance ips
        port = str(num + 5900)
        inst = user + ":" + inst_ip + ":" + port # cs123-newellz2:10.0.123.10:5901
        instances.append(inst)
        host += 1
        num += 1
    
    return instances
        
# start container instances with systemd
def create_instances(usernames):
    
    for user in usernames:
        # testcont@.service starts cont@.service and checks networking
        depinst = f"cont@{user}.service"
        # reload in case unit changed
        subprocess.run(["systemctl", "daemon-reload"], stdout=PIPE)
        # stop cont instance in case already running
        subprocess.run(["systemctl", "stop", depinst], stdout=PIPE)
        # only need to stop services and super units that remain after exit
        # testcont stops after initial run, any start command will completely restart
        
        instance = f"testcont@{user}.service"
        
        # start testcont for instance (starts cont for instance)
        p = subprocess.run(["systemctl", "start", instance], stdout=PIPE)
        if p.returncode == 0:
            logger.info("Container " + depinst + " created for " + user)
        else:
            logger.info("Error creating container for " + user)

def main():
    with open(args.passwd_list.name) as fin:
        usernames = [line.split(':')[0] for line in fin]

    course = usernames[0].split("-")[0]
    
    br = create_br_config(course)

    instances = create_inst_config(br[1], usernames)
    
    create_instances(usernames)

    # create file with list of instnace name:ip for each user
    filename = course + "/" + course + "-conts.txt"
    with open(filename, 'w') as fout:
        fout.write("\n".join(inst for inst in instances))
    
    print(f"\n\t file created: {filename} \n")


if __name__ == "__main__":
    main()
