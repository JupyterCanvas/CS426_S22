# Systemd config

---

## Simple service example.service
```bash
apt install cowsay
PATH=$PATH:/usr/games
```
```bash
vim /etc/systemd/system/example.service
```
```bash
[Unit]
Description=a simple service

[Service]
Type=simple
ExecStart=/etc/systemd/system/scripts/time.sh

[Install]
WantedBy=multi-user.target
```
```bash
vim /etc/systemd/system/scripts/time.sh
```
```bash
#!/bin/sh

echo $(date) | /usr/games/cowsay
```
```bash
systemctl start example.service
systemctl status example.service
```
```bash
● example.service - a simple service
     Loaded: loaded (/etc/systemd/system/example.service; disabled; vendor preset: enabled)
     Active: inactive (dead)

Mar 13 21:17:26 jupytercanvas systemd[1]: Started a simple service.
Mar 13 21:17:26 jupytercanvas time.sh[129284]:  _________________________________
Mar 13 21:17:26 jupytercanvas time.sh[129284]: < Sun 13 Mar 2022 09:17:26 PM PDT >
Mar 13 21:17:26 jupytercanvas time.sh[129284]:  ---------------------------------
Mar 13 21:17:26 jupytercanvas time.sh[129284]:         \   ^__^
Mar 13 21:17:26 jupytercanvas time.sh[129284]:          \  (oo)\_______
Mar 13 21:17:26 jupytercanvas time.sh[129284]:             (__)\       )\/\
Mar 13 21:17:26 jupytercanvas time.sh[129284]:                 ||----w |
Mar 13 21:17:26 jupytercanvas time.sh[129284]:                 ||     ||
Mar 13 21:17:26 jupytercanvas systemd[1]: example.service: Succeeded.
```
---
~~systemd service template to launch course bridge instances~~
---
---
~~systemd service template to create network namespace~~
---
---
~~systemd service template to setup networking in network namespaces~~
---
---
~~systemd service template to test networking in namespaces~~
---
---
~~Link instance service dependencies:~~
---
---
~~simple systemd service template to generate a container instance from an image~~
---
---
~~generate a container instance as an unprivledged user~~
---
---
~~generate container instance as user in user network namespace~~
---
---
Singularity rootless containers created with fakeroot option cannot use custom network namespace. Modified to use Singularity generated cni network config instead of manually creating network namespaces and container networking. 

---
## simple systemd service template to generate a container instance from an image

- Can't access systemd inside of container (for systemctl restart jupyter)
- Can run services such as vncserver or jupyter, but won't be able to manage them (become orphans)
### To run services in a SingularityCE container, use instances that run in the background:
```bash
vim /etc/systemd/system/cont@.service
```
```bash
[Unit]
Description=Generate container instance

[Service]
# forking because 'instance start' starts an instance and exits
Type=forking
# consider the unit to be active if the start action exited successfully
RemainAfterExit=yes

# start singularity instance
ExecStart=/usr/local/bin/singularity instance start /data/containers/alpine_latest.sif inst-%i

# stop singularity instance
ExecStop=/usr/local/bin/singularity instance stop inst-%i
```
```bash
# start instance
systemctl start cont@test123.service
# check
systemctl status cont@test123.service
singularity instance list
singularity shell instance://inst-test123
cat /etc/os-release
# stop instance
systemctl stop cont@test123.service
# check
singularity instance list
systemctl status cont@test123.service
```
---
## generate a container instance as an unprivledged user

- Add user to container service template:
```bash
vim /etc/systemd/system/cont@.service
```
```bash
# in [Service] section:
User=cs123-newellz2
```
```bash
# reload config
systemctl daemon-reload
systemctl start cont@123.service
systemctl status cont@123.service
# Instances started by another user won't be listed when singularity list called by root:
singularity instance list # no results
# Instances are linked with the user account that started them:
su cs123-newellz2
singularity instance list # shows inst-123 instance
singularity shell instance://inst-123
whoami
exit # from container
exit # from user (back to root)
```
---
## systemd service template to create fakeroot user containers
```bash
vim /etc/systemd/system/cont@.service
```
```bash
# in [Service] section: 

# containers/inst-username.conf stores ip:
# IP="IP=10.0.123.10"
EnvironmentFile=/etc/systemd/system/containers/inst-%i.conf

# run as user
#User=cs123-newellz2
# can't set user with environment file, has to be with %i
User=%i

# add fakeroot and network config to ExecStart: 
ExecStart=/usr/local/bin/singularity instance start --fakeroot --net --network-args ${IP} /data/containers/alpine_latest.sif inst-%i
```
```bash
systemctl start cont@cs123-newellz2.service
systemctl status cont@cs123-newellz2.service
```
```bash
● cont@cs123-newellz2.service - Generate fakeroot container instance with IP in own network namespace
     Loaded: loaded (/etc/systemd/system/cont@.service; static)
     Active: active (running) since Sat 2022-03-19 14:33:50 PDT; 5s ago
    Process: 190810 ExecStart=/usr/local/bin/singularity instance start --fakeroot --net --network-args ${IP} /data/containers/alpine_latest.sif inst-cs123->
   Main PID: 190857 (starter-suid)
      Tasks: 15 (limit: 2301)
     Memory: 24.4M
        CPU: 210ms
     CGroup: /system.slice/system-cont.slice/cont@cs123-newellz2.service
             ├─190857 Singularity instance: cs123-newellz2 [inst-cs123-newellz2]
             └─190858 sinit

Mar 19 14:33:50 jupytercanvas systemd[1]: Starting Generate fakeroot container instance with IP in own network namespace...
Mar 19 14:33:50 jupytercanvas singularity[190810]: INFO:    Converting SIF file to temporary sandbox...
Mar 19 14:33:50 jupytercanvas singularity[190810]: INFO:    instance started successfully
Mar 19 14:33:50 jupytercanvas systemd[1]: Started Generate fakeroot container instance with IP in own network namespace.
```
```bash
sudo -u cs123-newellz2 singularity instance list
#
INSTANCE NAME          PID       IP             IMAGE
inst-cs123-newellz2    190858    10.0.123.10    /tmp/rootfs-2963793288/root
```
```bash
sudo -u cs123-newellz2 singularity exec instance://inst-cs123-newellz2 whoami
# output: 
root
```
```bash
sudo -u cs123-newellz2 singularity exec instance://inst-cs123-newellz2 ip a
# output: 
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0@if150: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP
    link/ether fe:ca:70:32:1e:34 brd ff:ff:ff:ff:ff:ff
    inet 10.0.123.10/24 brd 10.0.123.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::fcca:70ff:fe32:1e34/64 scope link
       valid_lft forever preferred_lft forever
```
```bash
sudo -u cs123-newellz2 singularity exec instance://inst-cs123-newellz2 ping google.com -c1 
# output:
PING google.com (142.250.72.142): 56 data bytes
64 bytes from 142.250.72.142: seq=0 ttl=127 time=36.989 ms

--- google.com ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 36.989/36.989/36.989 ms
```
---
## systemd service template to test networking in containers
```bash
vim /etc/systemd/system/testcont@.service
```
```bash
[Unit]
Description=Test container networking

[Service]
# pings google.com from inside container to test network config
ExecStart=/etc/systemd/system/scripts/pingcow.sh %i
```
```bash
systemctl start testcont@cs123-newellz2.service
systemctl status testcont@cs123-newellz2.service
```
```bash
● testcont@cs123-newellz2.service - Test container networking
     Loaded: loaded (/etc/systemd/system/testcont@.service; static)
     Active: inactive (dead)

Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]: / cs123-newellz2 is root in container \
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]: | ping google.com from container ip   |
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]: \ (10.0.123.10/24): 0% packet loss    /
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]:  -------------------------------------
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]:         \   ^__^
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]:          \  (oo)\_______
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]:             (__)\       )\/\
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]:                 ||----w |
Mar 19 14:35:01 jupytercanvas pingcow.sh[191040]:                 ||     ||
Mar 19 14:35:01 jupytercanvas systemd[1]: testcont@cs123-newellz2.service: Succeeded.
```
---
## Link instance service dependencies:

- Use systemd BindTo+After in testcont service to link instance dependencies:
```bash
vim /etc/systemd/system/testcont@.service
```
```bash
# in [Unit]
# Ensure container is configured
# Generates container if it does not exist
BindsTo=cont@%i.service
After=cont@%i.service
```
```bash 
# delete existing containers
./cleanup/05-remove_containers.py cs123/cs123-pass.txt
# generate containers and test network config
systemctl start testcont@cs123-newellz2
systemctl status testcont@cs123-newellz2
```
```bash
● testcont@cs123-newellz2.service - Test container networking
     Loaded: loaded (/etc/systemd/system/testcont@.service; static)
     Active: inactive (dead)

Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]: / cs123-newellz2 is root in container \
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]: | ping google.com from container ip   |
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]: \ (10.0.123.10/24): 0% packet loss    /
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]:  -------------------------------------
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]:         \   ^__^
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]:          \  (oo)\_______
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]:             (__)\       )\/\
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]:                 ||----w |
Mar 19 14:35:50 jupytercanvas pingcow.sh[191324]:                 ||     ||
Mar 19 14:35:50 jupytercanvas systemd[1]: testcont@cs123-newellz2.service: Succeeded.
```
```bash
systemctl status cont@cs123-newellz2.service
```
```bash
● cont@cs123-newellz2.service - Generate fakeroot container instance with IP in own network namespace
     Loaded: loaded (/etc/systemd/system/cont@.service; static)
     Active: active (running) since Sat 2022-03-19 14:35:50 PDT; 37s ago
    Process: 191138 ExecStart=/usr/local/bin/singularity instance start --fakeroot --net --network-args ${IP} /data/containers/alpine_latest.sif inst-cs123->
   Main PID: 191186 (starter-suid)
      Tasks: 16 (limit: 2301)
     Memory: 18.6M
        CPU: 208ms
     CGroup: /system.slice/system-cont.slice/cont@cs123-newellz2.service
             ├─191186 Singularity instance: cs123-newellz2 [inst-cs123-newellz2]
             └─191187 sinit

Mar 19 14:35:49 jupytercanvas systemd[1]: Starting Generate fakeroot container instance with IP in own network namespace...
Mar 19 14:35:49 jupytercanvas singularity[191138]: INFO:    Converting SIF file to temporary sandbox...
Mar 19 14:35:50 jupytercanvas singularity[191138]: INFO:    instance started successfully
Mar 19 14:35:50 jupytercanvas systemd[1]: Started Generate fakeroot container instance with IP in own network namespace.
```
`systemctl start testcont@cs123-newellz2.service` starts: 
- an instance of the testcont service
- it also creates a cont#cs123-newellz.service instance
- only call the sub unit service and its dependencies are generated automatically
---

