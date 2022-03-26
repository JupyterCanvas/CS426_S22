#!/usr/bin/env python3

# Sends email to Canvas user with their instance url
# ./send_canvas_email.py cs123/cs123-netids.txt cs123/cs123-urls.txt
# (run get_enrollments.py to generate netid list file)
# (run create_urls.py to generate url list file)

import json # requests to Canvas api return json objects
import sys # for sys.exit, sys.argv
import pprint # pretty print python data structures
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
        Send email to Canvas user with their instance url
        '''),
        epilog='\
        ')

parser.add_argument('netid_list', type=argparse.FileType('r'),
                    help='List of user netids in a text file \
                    run get_enrollments.py to generate')

parser.add_argument('url_list', type=argparse.FileType('r'), 
                    help='List of container urls in a text file \
                    run create_urls.py to generate cs123/cs123-urls.txt')
            
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


# access token needed: 
# on your canvas page, go to Account, Settings, Approved Integrations to
# generate an access token. 

# student employee as teacher cannot add/remove or retrieve some student info,
# can get some info about course like section id

# get Zach to create an expiring token, put in local_settings.py file as: 
# ACCESS_TOKEN="your access token string"
# (we don't want access tokens in repository code!)
try:
    from local_settings import *
except ImportError:
    pass


BASE_URL = "https://canvas.instructure.com" 
ACCOUNT_ID = "44240000000000034" # College of Engineering 
# this is hardcoded for development: 
#COURSE_ID = "44240000000083090" # Jupyter Canvas course

def get_course_name(base_url, course_id, headers):
    #GET /api/v1/courses/:id
    url = f"{base_url}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)
    json_content = json.loads(response.content)
    return json_content['name']

def get_user(base_url, account_id, sis_uid, headers):
    # bug found: search for "vle" returns anything that start with vle: 
    # almost sent email to a Viktoriya instead of Vinh 
    
    # Queries search on SIS ID, login ID, name, or email address
    # search with login_in does not force exact match, sis_user_id does
    # need to add sis_user_id to course/course-netids.txt list <-- done.
    
    user_id = None
    if sis_uid is None or sis_uid == "":
        return user_id
    #GET /api/v1/accounts/:account_id/users
    url = f"{base_url}/api/v1/accounts/{account_id}/users"
    data = {"search_term" : sis_uid}
    response = requests.get(url, headers=headers, data=data)
    json_content = json.loads(response.content)
    #pprint.pprint(json_content)
    return json_content

def send_email(base_url, user_id, subject, body, context, headers):
    #POST /api/v1/conversations 
    url = f"{base_url}/api/v1/conversations"
    data = {
        'recipients[]': user_id,
        'force_new': True,
        'subject': subject,
        'body': body,
        'context_code': context
    }
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 201: 
        sent = True
    else: 
        sent = False

    return sent

def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}
    
    with open(args.netid_list.name) as fin:
        netids = [netid.strip() for netid in fin]

    # get canvas course id from netid list header: 
    # netids[0] = COURSE:course_id:timestamp
    course_id = netids[0].split(':', 2)[1]
    
    course_name = get_course_name(BASE_URL, course_id, headers)
    
    subject = course_name + ' Container URL'

    # context sets the course title used in email messages (otherwise randomly
    # assigns a course name that instructor is associated with): 
    # Zachary Newell (FERPA Training and Engineering Student Resources 2021 - 2022) just sent you a message in Canvas.
    # Zachary Newell (Project Jupyter) just sent you a message in Canvas.
    context = "course_" + course_id
    
    # remove role lines i.e. "# insructors:" from list
    ids = [n for n in netids[1:] if not n.startswith('#')]
    
    with open(args.url_list.name) as fin:
        # trim course prefix from url list to get netid:url list
        urls = [url.strip().split('-', 1)[1] for url in fin]
   
    # create new list: sis_id:url from ids list (netid:sis_id) and urls list (netid:url)
    data = []
    for i in ids: 
        for u in urls: 
            if i.split(':')[0] == u.split(':', 1)[0]: 
                sis_uid = i.split(':')[1]
                url = u.split(':', 1)[1]
                datastr = sis_uid + ":" + url
                data.append(datastr)
                break

    # generate personalized body of message and send to each user: 
    for d in data: 
        sis_uid = d.split(':', 1)[0]
        url = d.split(':', 1)[1]
        user = get_user(BASE_URL, ACCOUNT_ID, sis_uid, headers)

        for f in user: 
            user_name = f['name']
            if f['sis_user_id'] == sis_uid:
                user_id = f['id']
       
        first_name = user_name.split()[0]
       
        body = f"""
        {first_name}, 

        Your {course_name} container URL is: {url}

        Do not share this URL with anyone.

        Email us at eccstaff@engr.unr.edu if you have any issues accessing your container. 

        Best, 

        ECC staff
        """
        # hardcoded to my user_id for development, sends all emails to my Canvas account
        # with the personalization created for each user
        user_id = '44240000000078461'
        
        sent = send_email(BASE_URL, user_id, subject, body, context, headers)
        if sent: 
            logger.info("Container URL email sent to " + user_name + " in " + course_name)
        else: 
            logger.info("Error sending Container URL email to " + user_name + " in " + course_name)


if __name__ == "__main__":
    main()
