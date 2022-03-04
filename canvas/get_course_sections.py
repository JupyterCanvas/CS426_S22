#!/usr/bin/env python3

# Returns list of section ids from course id
# ./get_course_sections course_id#
# (run find_course_id.py to get course_id#)

import json # requests to Canvas api return json objects
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
        Find Canvas course section ids with course id:
          (run find_course_id.py to get the course id #)
        '''),
        epilog='Copy section id #s from the results. \
        ')

parser.add_argument('course_id', type=int,
                    help='Canvas course id #. \
                    Run find_course_id.py to get #')
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
#COURSE_ID = "44240000000083090" # Jupyter Canvas course


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


def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}

    course_id = args.course_id

    # Print course and section info: 
    print('\n')

    course = get_course_info(BASE_URL, course_id, headers)
    #pprint.pprint(course)
    print(f"\tCOURSE_ID  : {course['id']} : {course['name']}\n")

    sections = get_course_sections(BASE_URL, course_id, headers)
    #pprint.pprint(sections)
    for s in range(len(sections)):
        print(f"\tSECTION_ID : {sections[s]['id']} : {sections[s]['name']}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()

