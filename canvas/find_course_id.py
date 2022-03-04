#!/usr/bin/env python3

# Returns list of course ids from provided search term
# ./find_course_id search term

import json # requests to Canvas api return json objects
import re # for regular expression matching (in pagination)
import sys # for sys.exit, sys.argv
import pprint # pretty print python data structures
import logging 
import requests # to send HTTP requests with Python
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help

# setup CLI args and help
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Find Canvas course id with search term:
          the partial course name, subject or number.
          Must be at least 3 characters.
        '''),
        epilog='Copy the correct course id # from the results \
        ')

parser.add_argument('searchterm', type=str, nargs='+',
                    help='the string to search for \
                    such as "CS 426" or "senior projects"')
args = parser.parse_args()

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

# put in local_settings.py file as: 
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
    more = True
    courses = []
    #GET /api/v1/accounts/:account_id/courses
    next_url = f"{base_url}/api/v1/accounts/{account_id}/courses"
    
    while more:
        print('Making request...')
        #Requests that return multiple items paginated to 10 items by default.
        #set a custom per-page amount with the ?per_page parameter (limit=100)
        data = {"search_term" : search_term, "per_page" : 50}
        response = requests.get(next_url, headers=headers, data=data)
        if response.status_code != 200:
            logging.error(f"status_code: {response.status_code}, {response.text}")
            print('Exiting')
            sys.exit(1)
        json_results = response.json()
        courses = courses + response.json()

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

    return courses


def main():
    #search_term = args.searchterm
    search_term = ' '.join(sys.argv[1:])
    
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}
    #logging.info(headers)

    # find course id:
    #courses = get_course_id(BASE_URL, ACCOUNT_ID, "cs 135", headers)
    courses = get_course_id(BASE_URL, ACCOUNT_ID, search_term, headers)
    #pprint.pprint(courses)
    for c in range(len(courses)):
        print(f"\t{c}. COURSE_ID : {courses[c]['id']} : {courses[c]['name']}\n")
    sys.exit(0)

if __name__ == "__main__":
    main()

