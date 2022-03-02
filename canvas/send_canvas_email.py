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


def get_user_id(base_url, account_id, netid, headers):
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
    for u in json_content:
        if u['login_id'] == netid:
            user_id = u['id']
    return user_id

def send_email(base_url, user_id, subject, body, headers):
    #POST /api/v1/conversations 
    url = f"{base_url}/api/v1/conversations"
    data = {
        'recipients[]': user_id,
        'force_new': True,
        'subject': subject,
        'body': body,
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    print(response.status_code)
    print(response.text)


def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}
    
    netid = "sskidmore"
    user_id = get_user_id(BASE_URL, ACCOUNT_ID,  netid, headers)

    url = "http://192.168.161.139/mynovnc/vnc.html?path=/websockify?token=token1"
    
    subject = "Container URL"
    
    body = f"""
        {user_id}, 

        Your container URL is: {url}

        **Do not share this URL with anyone.**

        Email us at eccstaff@engr.unr.edu if you have any issues accessing your container. 

        Best, 

        ECC staff
    """
    
    send_email(BASE_URL, user_id, subject, body, headers)

    sys.exit(0)


if __name__ == "__main__":
    main()
