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
## Add users to server from list of netids:
```bash
./04-add_users.py
# prompts user for netID list:
usage: 04-add_users.py [-h] netid_list
04-add_users.py: error: the following arguments are required: netid_list
```
```bash
./04-add_users.py -h
# provides help flag:
usage: 04-add_users.py [-h] netid_list

Add users to server from list of netids
  (run get_course_enrollments.py to generate list file)
  Generates:
    user accounts on server per course
    user subuid/subgid mapping for container fakeroot
    user home directories
    temporary passwords that users must change at first login

positional arguments:
  netid_list  List of user netids in a text file Run get_enrollments.py to generate

optional arguments:
  -h, --help  show this help message and exit

To prevent accidental clobbering between course containers,
usernames are netids prepended with the course: cs123-sskidmore
```
output:
```bash
./04-add_users.py cs123/cs123-netids.txt
Added user: cs123-newellz2
Added user: cs123-sskidmore
Added user: cs123-zestreito
Added user: cs123-fgreen
Added user: cs123-vle
Added temporary user passwords for cs123
passwd: password expiry information changed.
User must change password at next login: cs123-newellz2
passwd: password expiry information changed.
User must change password at next login: cs123-sskidmore
passwd: password expiry information changed.
User must change password at next login: cs123-zestreito
passwd: password expiry information changed.
User must change password at next login: cs123-fgreen
passwd: password expiry information changed.
User must change password at next login: cs123-vle

         file created: cs123/cs123-pass.txt
```
creates list of usernames and temporary passwords:
```bash
cat cs123/cs123-pass.txt
```
```bash
cs123-newellz2:=reshActor71
cs123-sskidmore:ol!vePie73
cs123-zestreito:oldS3al24
cs123-fgreen:d@mpWater31
cs123-vle:spicyE)ge96
```
forces user to set password at next login:
```bash
login cs123-newellz2
Password:
You are required to change your password immediately (administrator enforced).
Changing password for cs123-newellz2.
Current password:
```
### Script to delete users (undo add_users.py script):
```bash
./scripts/04-cleanup_delusers.py -h
usage: 04-cleanup_delusers.py [-h] netid_list

Delete users from server from list of netids
  (run get_course_enrollments.py to generate list file)
  removes user account, user group, user home
  for future implementation, need to not remove
  subuid and subgid mapping but deactivate instead.

positional arguments:
  netid_list  List of user netids in a text file

optional arguments:
  -h, --help  show this help message and exit
```
```bash
./scripts/04-cleanup_delusers.py cs123/cs123-netids.txt
# output:
Removed user: cs123-newellz2
Removed user: cs123-sskidmore
Removed user: cs123-zestreito
Removed user: cs123-fgreen
Removed user: cs123-vle
```
---
## Setup systemd service templates, see [Systemd Config](systemd/README.md)
---
~~Create user network namespaces with systemd instances~~ 
---
Singularity rootless containers created with fakeroot option cannot use custom network namespace. Modified to use Singularity generated cni network config instead of manually creating network namespaces and container networking. 

---
## Create user container instances with systemd 
```bash
./05-create_containers.py
#
usage: 05-create_containers.py [-h] passwd_list
05-create_containers.py: error: the following arguments are required: passwd_list
```
```bash 
./05-create_containers.py -h
#
usage: 05-create_containers.py [-h] passwd_list

Create user containers from list of usernames:
  (run add_users.py to generate passwd_list)
  Generates:
    cni config for course subnet bridge
    user container config files
    user container instance services
    service to test networking config in user containers
    text file with list of usernames and container ips: cs135/cs135-conts.txt

positional arguments:
  passwd_list  List of usernames in a text file run add_users.py to generate cs123/cs123-pass.txt

optional arguments:
  -h, --help   show this help message and exit

Run systemctl status testcont@username.service to check container networking
```
output: 
```bash
./05-create_containers.py cs123/cs123-pass.txt
#
Container testcont@cs123-newellz2.service created for cs123-newellz2
Container testcont@cs123-sskidmore.service created for cs123-sskidmore
Container testcont@cs123-zestreito.service created for cs123-zestreito
Container testcont@cs123-fgreen.service created for cs123-fgreen
Container testcont@cs123-vle.service created for cs123-vle

         file created: cs123/cs123-conts.txt
```
creates list of usernames and container ips: 
```bash 
cat cs123/cs123-conts.txt
#
cs123-newellz2:10.0.123.10
cs123-sskidmore:10.0.123.11
cs123-zestreito:10.0.123.12
cs123-fgreen:10.0.123.13
cs123-vle:10.0.123.14
```
```bash 
# check network config of container instances: 
systemctl status testcont@cs123-newellz2.service
● testcont@cs123-newellz2.service - Test container networking
     Loaded: loaded (/etc/systemd/system/testcont@.service; static)
     Active: inactive (dead)

Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]: / cs123-newellz2 is root in container \
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]: | ping google.com from container ip   |
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]: \ (10.0.123.10/24): 0% packet loss    /
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]:  -------------------------------------
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]:         \   ^__^
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]:          \  (oo)\_______
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]:             (__)\       )\/\
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]:                 ||----w |
Mar 19 14:02:40 jupytercanvas pingcow.sh[189334]:                 ||     ||
Mar 19 14:02:40 jupytercanvas systemd[1]: testcont@cs123-newellz2.service: Succeeded.
```
---
### Script to remove containers (undo create_containers.py script)
```bash
./cleanup/05-remove_containers.py -h
#
usage: 05-remove_containers.py [-h] passwd_list

Remove containers created with create_containers.py

positional arguments:
  passwd_list  List of usernames in a text file run add_users.py to generate cs123/cs123-pass.txt

optional arguments:
  -h, --help   show this help message and exit
```
output: 
```bash
./cleanup/05-remove_containers.py cs123/cs123-pass.txt
#
Container cont@cs123-newellz2.service stopped
Container cont@cs123-sskidmore.service stopped
Container cont@cs123-zestreito.service stopped
Container cont@cs123-fgreen.service stopped
Container cont@cs123-vle.service stopped
```
---

