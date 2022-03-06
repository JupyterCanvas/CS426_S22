# Create user containers from Canvas course data

## 01-find_course_id.py: 
### Find Canvas course id with search term     
```bash
./01-find_course_id.py -h
'''
usage: 01-find_course_id.py [-h] searchterm [searchterm ...]

Find Canvas course id with search term:
  the partial course name, subject or number.
  Must be at least 3 characters.

positional arguments:
  searchterm  the string to search for such as "CS 426" or "senior projects"

optional arguments:
  -h, --help  show this help message and exit

Copy the correct course id # from the results
'''

./01-find_course_id.py jup
'''
Making request...


        0. COURSE_ID : 44240000000083090 : Project Jupyter
'''
```
---
## 02-get_course_sections.py: 
### Find Canvas course section ids with course id:    
```bash
./02-get_course_sections.py -h
'''
usage: 02-get_course_sections.py [-h] course_id

Find Canvas course section ids with course id:
  (run find_course_id.py to get the course id #)

positional arguments:
  course_id   Canvas course id #. Run find_course_id.py to get #

optional arguments:
  -h, --help  show this help message and exit

Copy section id #s from the results.
'''

./02-get_course_sections.py 44240000000083090
'''

        COURSE_ID  : 44240000000083090 : Project Jupyter

        SECTION_ID : 44240000000088893 : Project Jupyter
'''
```
---
## 03-get_course_enrollments.py: 
### Find Canvas course enrolled netids with course id:
```bash
./03-get_course_enrollments.py -h
'''
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
'''

./03-get_course_enrollments.py 44240000000083090
'''
Making request...

         file created: cs123/cs123-netids.txt
'''

cat cs123/cs123-netids.txt
'''
cs123:44240000000083090:22-03-05 08:10 PM
# instructors:
newellz2
sskidmore
zestreito
# tas:
fgreen
# students:
vle
'''
```
---
## 04-add_users.py: 
### Add users to server from list of netids:         
```bash
./04-add_users.py -h
'''
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
'''

./04-add_users.py cs123/cs123-netids.txt
'''
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
'''

cat cs123/cs123-pass.txt
'''
cs123-newellz2:slowAppl373
cs123-sskidmore:th!nGrain73
cs123-zestreito:itchyC@nary20
cs123-fgreen:o)dBear23
'''

login cs123-sskidmore
'''
Password:
You are required to change your password immediately (administrator enforced).
Changing password for cs123-sskidmore.
Current password:
'''
```
---
## 05-create_exchange.py: 
### Create exchange directory for nbgrader     
```bash
./05-create_exchange.py -h
'''
usage: 05-create_exchange.py [-h] netid_list

Create exchange directory for nbgrader

positional arguments:
  netid_list  Text file, COURSE in header. Run get_course_enrollments to generate.

optional arguments:
  -h, --help  show this help message and exit
'''

./05-create_exchange.py cs123/cs123-netids.txt
'''

         Exhange directory created for cs123 at cs123/exchange
'''
ls -l cs123/
'''
-rw-r--r-- 1 root root  116 Mar  5 20:10 cs123-netids.txt
-rw-r--r-- 1 root root  129 Mar  5 20:12 cs123-pass.txt
drwxrwxrwx 2 root root 4096 Mar  5 20:15 exchange
'''
```
---
## 06-create_namespaces.py: 
### Create network namespaces for user containers:
```bash
./06-create_namespaces.py -h
'''
usage: 06-create_namespaces.py [-h] passwd_list

Create network namespaces for user containers

positional arguments:
  passwd_list  List of usernames in a text file run add_users.py to generate cs123/cs123-pass.txt

optional arguments:
  -h, --help   show this help message and exit

To enable ip forwarding and nat for network access in container
server should have the following set:
(this is ephemeral, should change to persistent/load at boot)

    sysctl -w net.ipv4.ip_forward=1
    iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE

check with:
    sysctl net.ipv4.ip_forward
    iptables -L -t nat -v -n
'''

./06-create_namespaces.py cs123/cs123-pass.txt
'''
Bridge br-cs123 created for cs123, ip=10.0.123.1/24
Namespace ns-cs123-newellz2 created with ip: 10.0.123.10/24
Namespace ns-cs123-sskidmore created with ip: 10.0.123.11/24
Namespace ns-cs123-zestreito created with ip: 10.0.123.12/24
Namespace ns-cs123-fgreen created with ip: 10.0.123.13/24
Namespace ns-cs123-vle created with ip: 10.0.123.14/24

         file created: cs123/cs123-netns.txt
'''

cat cs123/cs123-netns.txt
'''
ns-cs123-newellz2:10.0.123.10/24
ns-cs123-sskidmore:10.0.123.11/24
ns-cs123-zestreito:10.0.123.12/24
ns-cs123-fgreen:10.0.123.13/24
ns-cs123-vle:10.0.123.14/24
'''

ping 10.0.123.10 -c2
'''
PING 10.0.123.10 (10.0.123.10) 56(84) bytes of data.
64 bytes from 10.0.123.10: icmp_seq=1 ttl=64 time=0.022 ms
64 bytes from 10.0.123.10: icmp_seq=2 ttl=64 time=0.045 ms

--- 10.0.123.10 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1021ms
rtt min/avg/max/mdev = 0.022/0.033/0.045/0.011 ms
'''

ip netns exec ns-cs123-newellz2 ping google.com -c2
'''
PING google.com (142.250.72.174) 56(84) bytes of data.
64 bytes from lax17s50-in-f14.1e100.net (142.250.72.174): icmp_seq=1 ttl=127 time=38.3 ms
64 bytes from lax17s50-in-f14.1e100.net (142.250.72.174): icmp_seq=2 ttl=127 time=38.1 ms

--- google.com ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 38.082/38.210/38.338/0.128 ms
'''

```
---
## 06-cleanup_creatns.py:
### Remove network namespaces created with create_namespaces.py:
```bash
./cleanup/06-cleanup_createns.py -h
'''
usage: 06-cleanup_createns.py [-h] netns_list

Remove network namespaces created with create_namespaces.py

positional arguments:
  netns_list  List of network namespaces in a text file run create_namespaces.py to generate cs123/cs123-netns.txt

optional arguments:
  -h, --help  show this help message and exit
'''

./cleanup/06-cleanup_createns.py cs123/cs123-netns.txt
'''
Bridge br-cs123 removed
Namespace ns-cs123-newellz2 removed
Namespace ns-cs123-sskidmore removed
Namespace ns-cs123-zestreito removed
Namespace ns-cs123-fgreen removed
Namespace ns-cs123-vle removed
'''
```
---
## 04-cleanup_delusers.py:
### Delete users from server from list of netids:
```bash
./cleanup/04-cleanup_delusers.py -h
'''
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
'''

./cleanup/04-cleanup_delusers.py cs123/cs123-netids.txt
'''
Removed user: cs123-newellz2
Removed user: cs123-sskidmore
Removed user: cs123-zestreito
Removed user: cs123-fgreen
Removed user: cs123-vle
'''
```
---
