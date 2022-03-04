#!/usr/bin/env python3
import json # requests to Canvas api return json objects
import sys # for sys.exit()
import pprint # pretty print python data structures
import logging 
import requests # to send HTTP requests with Python
import argparse # for adding CLI tags/help

# can setup CLI flags and help here
parser = argparse.ArgumentParser(
        description='',
        epilog='\
        ')
##parser.add_argument('searchterm', type=str, help='the string to search for')
##args = parser.parse_args()

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
COURSE_ID = "44240000000083090" # Jupyter Canvas course

def get_user(base_url, account_id, netid, headers):
    user_id = None
    netid = netid.strip()
    if netid is None or netid == "":
        return user_id
    #GET /api/v1/accounts/:account_id/users
    url = f"{base_url}/api/v1/accounts/{account_id}/users"
    data = {"search_term" : netid}
    response = requests.get(url, headers=headers, data=data)
    json_content = json.loads(response.content)
    #pprint.pprint(json_content)
    return json_content

def get_course_name(base_url, course_id, headers):
    #GET /api/v1/courses/:id
    url = f"{base_url}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)
    json_content = json.loads(response.content)
    return json_content['name']

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
    #print(response.status_code)
    #print(response.text)


def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}
    
    course_name = get_course_name(BASE_URL, COURSE_ID, headers)
    
    netid = "sskidmore"
    user = get_user(BASE_URL, ACCOUNT_ID,  netid, headers)
    for u in user: 
        user_name = u['name']
        if u['login_id'] == netid:
            user_id = u['id']
    first_name = user_name.split()[0]

    url = "http://192.168.161.139/mynovnc/vnc.html?path=/websockify?token=token1"
    
    subject = course_name + ' Container URL'

    body = f"""
        {first_name}, 

        Your {course_name} container URL is: {url}

        Do not share this URL with anyone.

        Email us at eccstaff@engr.unr.edu if you have any issues accessing your container. 

        Best, 

        ECC staff
    """
    # context sets the course title used in email messages (otherwise randomly
    # assigns a course name that instructor is associated with): 
    # Zachary Newell (FERPA Training and Engineering Student Resources 2021 - 2022) just sent you a message in Canvas.
    # Zachary Newell (Project Jupyter) just sent you a message in Canvas.
    context = "course_" + COURSE_ID
    
    send_email(BASE_URL, user_id, subject, body, context, headers)

    sys.exit(0)


if __name__ == "__main__":
    main()
