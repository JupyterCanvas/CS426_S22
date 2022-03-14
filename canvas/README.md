
# Create user containers from Canvas Course data

## Find course id with search term: 
```bash
./01_find_course.py
# prompts user for search term: 
usage: 01_find_course.py [-h] searchterm [searchterm ...]
01_find_course.py: error: the following arguments are required: searchterm
```
```bash
./01_find_course.py -h
# provides help flag: 
usage: 01_find_course.py [-h] searchterm [searchterm ...]

Find Canvas course id with search term:
  the partial course name, subject or number.
  Must be at least 3 characters.

positional arguments:
  searchterm  the string to search for such as "CS 426" or "senior projects"

optional arguments:
  -h, --help  show this help message and exit

Copy the correct course id # from the results
```
```bash
./01_find_course.py jup
# search with at least 3 characters, spaces are ok, can search: cs 135
Making request...


        1. COURSE_ID : 44240000000083090 : Project Jupyter
```
> This needs initial administrator interaction for the selection of a course id, but we can assign course ids to users for subsequent use. 
---
## Find Canvas course section ids with course id:
```bash
./02-get_course_sections.py
# prompts user for course id:
usage: 02-get_course_sections.py [-h] course_id
02-get_course_sections.py: error: the following arguments are required: course_id
```
```bash
./02-get_course_sections.py -h
# provides help flag:
usage: 02-get_course_sections.py [-h] course_id

Find Canvas course section ids with course id:
  (run find_course_id.py to get the course id #)

positional arguments:
  course_id   Canvas course id #. Run find_course_id.py to get #

optional arguments:
  -h, --help  show this help message and exit

Copy section id #s from the results.
```
output: 
```bash
./02-get_course_sections.py  44240000000081158 # CS 447 has ugrad and grad sections: 


        COURSE_ID  : 44240000000081158 : Spring 2022 CS 447/647

        SECTION_ID : 44240000000083312 : CS 447.1002 - Computer Systems Admin - Spr22

        SECTION_ID : 44240000000083384 : CS 647.1001 - Computer Systems Admin - Spr22
```
> Can use section ids to pull enrollments by section instead of course to create resources customized by section
---
## Find Canvas course enrolled netids with course id:
```bash
./03-get_course_enrollments.py
# prompts user for course id:
usage: 03-get_course_enrollments.py [-h] course_id
03-get_course_enrollments.py: error: the following arguments are required: course_id
```
```bash
./03-get_course_enrollments.py -h
# provides help flag: 
usage: 03-get_course_enrollments.py [-h] course_id

Find Canvas course enrolled netids with course id:
  (run find_course_id.py to get the course id #)
  Generates:
    COURSE = subject and number string, i.e. "cs135"
    course directory in cwd: cs135/
    text file with list of enrolled netids: cs135/cs135-netids.txt
        file header = COURSE:course_id:timestamp
        netids grouped by role: instructors, tas, students

positional arguments:
  course_id   Canvas course id #. Run find_course_id.py to get #

optional arguments:
  -h, --help  show this help message and exit
```
output:
```bash
./03-get_course_enrollments.py 44240000000083090
Making request...

         file created: cs123/cs123-netids.txt
```
creates list of netids sorted by role: 
```bash
cat cs123/cs123-netids.txt
```
```bash
cs123:44240000000083090:22-03-13 08:03 PM
# instructors:
newellz2
sskidmore
zestreito
# tas:
fgreen
# students:
vle
```
---

