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
        Start websockify instances for users on server
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

def create_user_config(instances, course): 
    
    classconf = []
    wsports = []
    for inst in instances: 
        user = inst.split(':', 1)[0]
        vncport = int(inst.rsplit(':', 1)[1])
        wsport = str(vncport + 180)
        wsstr = user + ":" + wsport
        wsports.append(wsstr)

        # create systemd websockify service config
        filename = "/etc/systemd/system/containers/ws-" + user + ".conf"
        with open(filename, 'w') as fout: 
            fout.write("COURSE=" + course + "\nWSPORT=" + wsport)

        # create nginx user config
        userconf = f'''
location /{user}/ {{
        proxy_pass http://192.168.161.131:{wsport}/; # websockify from server
}}

location /{user}/websockify {{
        proxy_http_version 1.1;
        proxy_pass http://192.168.161.131:{wsport}/; # websockify from server
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        # VNC connection timeout
        proxy_read_timeout 61s;

        # Disable cache
        proxy_buffering off;
}}
'''     
        classconf.append(userconf)

    return [classconf, wsports]

def config_nginx(classconf, course):

    # write all nginx user configs to course config file (included in default server block)
    filename = "/etc/nginx/sites-available/containers/" + course + ".conf"
    with open(filename, 'w') as fout: 
        fout.write("\n".join(conf for conf in classconf))
    
    # check nginx config
    p = subprocess.run(["nginx", "-t"], stdout=PIPE)
    if p.returncode == 0:
        logger.info("nginx config passed check")
    else: 
        logger.info("error with nginx config, exiting.")
        sys.exit(0)

    # reload nginx
    p = subprocess.run(["systemctl", "reload", "nginx"], stdout=PIPE)
    if p.returncode == 0:
        logger.info("nginx reloaded")
    else: 
        logger.info("Error reloading nginx, exiting.")
        sys.exit(0)

def start_ws(wsports): 
    for w in wsports: 
        user = w.split(':')[0]
        wsport = w.split(':')[1]
        instance = f"ws@{user}.service"
        p = subprocess.run(["systemctl", "start", instance], stdout=PIPE)
        if p.returncode == 0: 
            logger.info("Websockify started for " + user + " on server, port: " + wsport)
        else: 
            logger.info("Error starting websockify for " + user + ".\n\
                    Check that port " + wsport + " is not already in use with 'ps aux | grep websockify'.\n\
                    If it is in use, use 'kill <pid>' to stop")



def main():
    with open(args.instance_list.name) as fin:
        instances = [inst.strip() for inst in fin]

    course = instances[0].split('-', 1)[0]

    userconfigs = create_user_config(instances, course)

    classconf = userconfigs[0]
    wsports = userconfigs[1]

    config_nginx(classconf, course)

    start_ws(wsports)




if __name__ == "__main__":
    main()
