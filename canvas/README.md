
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

