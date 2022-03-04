#!/usr/bin/env python3

# Creates text file:
# list of enrolled netids by role from course id
# ./get_course_enrollments course_id#
# (run find_course_id.py to get course_id#)

import json # requests to Canvas api return json objects
import re # for regular expression matching (in pagination)
import sys # for sys.exit, sys.argv
import pprint # pretty print python data structures
import logging 
import requests # to send HTTP requests with Python
import argparse # for adding CLI tags/help
import textwrap # for formatting argparse help
import os # mkdirs to recursively create directories
import datetime # add timestamp to generated file
from datetime import datetime, timedelta, tzinfo

# setup CLI args and help
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Find Canvas course enrolled netids with course id:
          (run find_course_id.py to get the course id #)
          Generates:
            COURSE = subject and number string, i.e. "CS135"
            course directory in cwd: CS135/
            text file with list of enrolled netids: CS135/CS135-netids.txt
                file header = COURSE:course_id:timestamp
                netids grouped by role: instructors, tas, students
        '''),
        epilog='\
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

# generate a course string like "CS135"
def get_course(base_url, course_id, headers): 
    #GET /api/v1/courses/:id
    url = f"{base_url}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)
    json_content = json.loads(response.content)
    #pprint.pprint(json_content)
    name = json_content['name']
    # find course "SUBJ ###" strings. 
    # CS/CPE are current subjects can expand to all CoEN subjs
    course = (re.search('CS \d\d\d|CPE \d\d\d', name).group(0))
    # remove whitespace
    course = course.replace(' ', '')
    return course.lower()


def main():
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=ACCESS_TOKEN)}

    course_id = args.course_id
    
    # timestamp: 22-03-04 05:18 AM
    date = datetime.now().strftime('%y-%m-%d %I:%M %p')

    # get course enrollments:
    enrollments = get_course_enrollments(BASE_URL, course_id, headers)

    # get netid for each enrollment:
    instructors = []
    tas = []
    #observers = []
    students = []
    for e in enrollments:
        netid = e["user"]["login_id"]
        if e["role"] == "TeacherEnrollment":
            instructors.append(netid)
        if e["role"] == "TaEnrollment":
            tas.append(netid)
        # ObserverEnrollment ?
        if e["role"] == "StudentEnrollment":
            students.append(netid)
    
    instructors.sort()
    tas.sort()
    students.sort()

    # get course name: 
#    course = get_course(BASE_URL, course_id, headers)
# tested, works with standard CS and CPE course naming conventions
# Jupyter Canvas course didn't follow std convention, hardcoding for JC: 
    course = "cs123"

    if not os.path.exists(course):
        os.makedirs(course)

    fout = course + "/" + course + "-netids.txt"
    with open(fout, "w") as f:
        f.write(course + ":" + str(course_id) + ":" + date + "\n")
        f.write("# instructors:\n")
        f.write("\n".join(n for n in instructors))
        f.write("\n# tas:\n")
        f.write("\n".join(n for n in tas))
        f.write("\n# students:\n")
        f.write("\n".join(n for n in students))
        f.write("\n")

    print(f"\n\t file created: {fout}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()

