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
# Engineering Student Resources course info:
COURSE_ID = "44240000000010317" # Engineering Student Resources 2020 - 2021
# for the Engineering Student Resources Canvas page, 
# account and course id should not change, but section id will 
# can create new sections for personalized announcements/quizzes
#SECTION_ID = "44240000000082022" # Engineering Student Resources 2021-2022
#SECTION_ID = "44240000000087254" # CEE Undergraduate Students

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


def add_user(base_url, account_id, netid, section_id, headers):
    user_id = get_user_id(base_url, account_id, netid, headers)
    if user_id is None:
        logging.error(f"{netid}: user_id is equal to None.")
#        print(netid) # need to create output file to append to
        return False
    logging.info(f"{netid}: {user_id}")

    #POST /api/v1/sections/:section_id/enrollments
    url = f"{base_url}/api/v1/sections/{section_id}/enrollments"
    data = {"enrollment[user_id]" : user_id,
            "enrollment[type]" : "StudentEnrollment",
            # If set to 'active,' student immediately enrolled in course.
            # Otherwise they will be required to accept a course invitation.
            # (will also be sent invitation if enroll manually with online gui)
            "enrollment[enrollment_state]" : "active",
            "per_page" : 100}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        logging.info(f"Successfully added {netid}")
    else:
        logging.error(f"Failed to add {netid}, status_code: {response.status_code}, {response.text}")


def remove_enrollment(base_url, course_id, enrollment_id, headers):
    #DELETE /api/v1/courses/:course_id/enrollments/:id
    #enrollment ids are tied to sections, you are deleting a section enrollment
    url = f"{base_url}/api/v1/courses/{course_id}/enrollments/{enrollment_id}"
    data = { "task" : "delete" }
    response = requests.delete(url, headers=headers, data=data)

    if response.status_code != 200:
        logging.error(f"Failed to remove enrollment, {enrollment_id}, text: {response.text}")


#must remove all enrollments from a section before deleting a section
def remove_all_from_section(base_url, course_id, section_id, headers):
    enrollments = get_course_enrollments(base_url, course_id, headers)
    for e in enrollments:
        section = str(e["course_section_id"])
        if section == section_id:
            print('found')
            enrollment_id = e["id"]
            remove_enrollment(base_url, course_id, enrollment_id, headers)
            logging.info(f"Deleting enrollment id: {enrollment_id}")


#if students removed but section not, check online GUI to see if you or a
#teacher is still enrolled in the section, will need to leave Zach as teacher
#b/c you can't delete yourself from section in online GUI.
def remove_section(base_url, course_id, section_id, headers):
    remove_all_from_section(base_url, course_id, section_id, headers)
    #DELETE /api/v1/sections/:id
    url = f"{base_url}/api/v1/sections/{section_id}"
    response = requests.delete(url, headers=headers)


def add_section(base_url, course_id, name, headers):
    #POST /api/v1/courses/:course_id/sections
    url = f"{base_url}/api/v1/courses/{course_id}/sections"
    data = {"course_section[name]" : name}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        logging.error("error adding section")
    json_content = json.loads(response.content)
    return json_content


def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}
    print('stub')
    sys.exit(0)

if __name__ == "__main__":
    main()

