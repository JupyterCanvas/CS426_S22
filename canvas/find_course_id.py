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

# find course id with search term: The partial course name, code, or full ID to
# match and return in the results list. Must be at least 3 characters.
def get_course_id(base_url, account_id, search_term, headers):
    #GET /api/v1/accounts/:account_id/courses
    url = f"{base_url}/api/v1/accounts/{account_id}/courses"
    data = {"search_term" : search_term}
    response = requests.get(url, headers=headers, data=data)
    json_content = json.loads(response.content)
    return json_content

def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}
    #logging.info(headers)

    # find course id:
    courses = get_course_id(BASE_URL, ACCOUNT_ID, "CS 381", headers)
    #pprint.pprint(courses)
    for c in range(len(courses)):
        print(f"\tCOURSE_ID : {courses[c]['id']} : {courses[c]['name']}\n")
    sys.exit(0)

if __name__ == "__main__":
    main()

