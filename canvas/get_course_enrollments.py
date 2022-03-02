#!/usr/bin/env python3

import json # requests to Canvas api return json objects
import re # for regular expression matching
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
#COURSE_ID = "44240000000080854" # CS 381 Spring 2022
COURSE_ID = "44240000000083090" # Jupyter Canvas course

def get_account_info(base_url, account_id, headers):
    #GET /api/v1/accounts/:id
    url = f"{base_url}/api/v1/accounts/{account_id}"
    response = requests.get(url, headers=headers)
    json_content = json.loads(response.content)
    return json_content

def get_course_info(base_url, course_id, headers):
    #GET /api/v1/courses/:id
    url = f"{base_url}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)
    json_content = json.loads(response.content)
    return json_content

def get_course_sections(base_url, course_id, headers):
    # GET /api/v1/courses/:course_id/sections
    url = f"{base_url}/api/v1/courses/{course_id}/sections"
    response = requests.get(url, headers=headers)
    json_content = json.loads(response.content)
    return json_content

def print_course_info(base_url, account_id, course_id, headers):

    account = get_account_info(base_url, account_id, headers)
    #pprint.pprint(account)
    print(f"\n\tACCOUNT_ID : {account['id']} : {account['name']}")

    course = get_course_info(base_url, course_id, headers)
    #pprint.pprint(course)
    print(f"\tCOURSE_ID  : {course['id']} : {course['name']}\n")

    sections = get_course_sections(base_url, course_id, headers)
    #pprint.pprint(sections)
    for s in range(len(sections)):
        print(f"\tSECTION_ID : {sections[s]['id']} : {sections[s]['name']}\n")

def get_course_enrollments(base_url, course_id, headers):
    more = True
    enrollments = []
    #GET /api/v1/courses/:course_id/enrollments
    next_url = f"{base_url}/api/v1/courses/{course_id}/enrollments"

    while more:
        print('Making request...')
        #Requests that return multiple items paginated to 10 items by default.
        #set a custom per-page amount with the ?per_page parameter (limit=100)
        #data = {"type[]" : "studentenrollment", "per_page" : 100}
        data = {"per_page" : 100}
        response = requests.get(next_url, headers=headers, data=data)
        if response.status_code != 200:
            logging.error(f"status_code: {response.status_code}, {response.text}")
            print('Exiting')
            sys.exit(1)
        json_results = response.json()
        enrollments = enrollments + response.json()

        # Handle Pagination
        link = response.headers.get('Link')
        links = link.split(',')
        next_url = None

        more = False
        for l in links:
            match = re.match(r'<(.*)>;\srel="next"', l)
            if match:
                more = True
                next_url = match.groups()[0]

    return enrollments

def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}

    # set found course id to COURSE_ID.
    # print course info:
    print_course_info(BASE_URL, ACCOUNT_ID, COURSE_ID, headers)

    # get course enrollments:
    enrollments = get_course_enrollments(BASE_URL, COURSE_ID, headers)

    # get netid for each enrollment:
    netids = []
    for e in enrollments:
        netid = e["user"]["login_id"]
        netids.append(netid)
    netids.sort()
    
    fout = "Jupyter_netids.txt"
    with open(fout, "w") as f:
        f.write("\n".join(n for n in netids))

    print(f"\n\t file created: {fout}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()

