#!/usr/bin/env python3

# Generate urls for user containers, start user vncservers
# ./create_urls.py CS123/CS123-conts.txt
# (run create_containers.py to generate instance list file)

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
        Create urls for users to access vnc web sessions of their containers: 
          (run create_containers.py to generate instance_list)
          Generates:
            user token for websockify url 
            course tokens file for websockify
            url for user to access vnc web session of container
            course index html file with user urls (for instructors)
            starts and tests vncservers in container instances
            text file with list of usernames and urls: cs135/cs135-urls.txt
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


def create_tokens(instances): 
    tokens = []
    usertokens = []
    for inst in instances: 
        user = inst.split(':', 1)[0]
        # inst = cs123-newellz2:10.0.123.10:5901, ip = 10.0.123.10, port = 5901
        ip = inst.split(':')[1]
        port = inst.split(':')[2]
        # ip = 10.0.123.10, token = 12310
        token_no = ''.join(ip.rsplit('.', 2)[1:])
        # token12310: 10.0.123.10:5901
        token = "token" + token_no
        tokenstr = token + ": " + ip + ":" + port
        tokens.append(tokenstr)
        # cs123-newellz2:token12310
        usertokenstr = user + ":" + token
        usertokens.append(usertokenstr)
        
    # ip = 10.0.123.10, subnet (3rd octet) = 123
    subnet = instances[0].rsplit('.', 2)[1]

    # create course token file
    filename = "/usr/local/websockify/token/t" + subnet
    
    with open(filename, 'w') as fout: 
        fout.write("\n".join(token for token in tokens))

    print(f"\n\t file created: {filename} \n")

    return usertokens

def create_urls(tokens):
    course = tokens[0].split("-")[0]
    urls = []
    for t in tokens:
        user = t.split(':', 1)[0]
        token = t.split(':', 1)[1]
        url = "http://192.168.161.131/" + user + "/vnc.html?path=" + user + "/websockify?token=" + token
        urlstr = user + ":" + url
        urls.append(urlstr)
    
    # create file with list of username:url for each user
    filename = course + "/" + course + "-urls.txt"
    with open(filename, 'w') as fout:
        fout.write("\n".join(url for url in urls))

    print(f"\n\t file created: {filename} \n")

    return urls

def create_index(urls): 
    course = urls[0].split("-")[0]
    #filename = course + "/" + course + "-index.html"
    filename = "/var/www/html/" + course + "-index.html"
    
    links = []
    for u in urls: 
        username = u.split(':', 1)[0]
        url = u.split(':', 1)[1]

        link = f'''
<a href="{url}">
  {username}
</a><br>'''
        links.append(link)

    with open(filename, 'w') as fout:
        fout.write("\n".join(link for link in links))
    
    print(f"\n\t file created: {filename} \n")

def start_vnc(instances):
    
    users = []
    for inst in instances: 
        user = inst.split(':', 1)[0]
        users.append(user)

    for user in users:
        instance = f"vnc@{user}.service"
        # reload in case unit changed
        subprocess.run(["systemctl", "daemon-reload"], stdout=PIPE)
        # stop instance in case already running 
        subprocess.run(["systemctl", "stop", instance], stdout=PIPE)
        # start vncserver for instance
        p = subprocess.run(["systemctl", "start", instance], stdout=PIPE)
        if p.returncode == 0:
            logger.info("VNC server started with " + instance)
        else:
            logger.info("Error starting VNC server with " + instance)
    
    # I think there is a race condition happening
    # 2-3 of the 5 vncserver services run less than 50 tasks
    # others run more than 70 tasks to fully setup vnc desktop
    # stopping and starting services with less than 50 tasks reported 
    # fixes the issue: 
    for user in users: 
        p = subprocess.run(["./fixvnc.sh", user], stdout=PIPE)
        if p.returncode == 0:
            logger.info("VNC server cheked for " + user)
        else:
            logger.info("Error checking VNC server for  " + user)
        


def main():
    with open(args.instance_list.name) as fin:
        instances = [inst.strip() for inst in fin]
    
    tokens = create_tokens(instances)
    
    urls = create_urls(tokens)

    create_index(urls)

    start_vnc(instances)

if __name__ == "__main__":
    main()
