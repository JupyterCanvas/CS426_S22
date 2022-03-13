
# Singularity container config
---
## create basic definition file

```bash
mkdir containers && cd containers
vim debian.def
```
```
Bootstrap: library
From: debian:bullseye

%post
    echo "Hello from inside the container"

%runscript
    echo "This is what happens when you run the container..."

```
---
development cycle:
1. create a writable container (sandbox)
2. shell into container with --writable option and tinker with it interactively
3. record changes in definition file
4. rebuild the container from the definition file
5. rinse and repeat until happy
6. rebuild the container from the final definition file as a read-only singularity image format (SIF) image for use in production

---
## 1. build sandbox
```bash
singularity build --sandbox debian debian.def
```

## 2. shell into container
```bash
singularity shell --writable debian
```
## ...start tinkering...
```bash
# in container:
> cat /etc/apt/sources.list
> vim sources.list # vim not found
```
***ISSUES:***

1. base container has anemic apt sources.list
2. vim not installed!

- > .DEF CHANGES:
(create files/sources.list) add files section, install vim in post:
```bash
%files
    files/sources.list /etc/apt

%post
    echo "Hello from inside the container"
    apt update
    apt install -y vim
```

---
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> apt upgrade
# get multiple errors related to debconf:
# debconf: unable to initialize frontend:
# debconf doesn't realize it's running non-interactively, trying to open dialog for user input

> export DEBIAN_FRONTEND=noninteractive
> apt upgrade

# debconf errors gone, gets farther in tzdata update, stalls at:
# perl: warning: Setting locale failed.
# perl: warning: Please check that your locale settings:
#        LANGUAGE = (unset),
#        LC_ALL = (unset),
#        LANG = "en_US.UTF-8"
#    are supported and installed on your system.
```
***ISSUES:***

3. need to set apt to noninteractive install
4. need to install and set locales
- > .DEF CHANGES: set noninteractive, install and configure locales:
```bash
%post
    echo "Hello from inside the container"

    # set apt to noninteractive install
    export DEBIAN_FRONTEND=noninteractive

    apt update && apt upgrade -y
    apt install -y vim \
        locales

    # set default locale
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen en_US.utf8
    update-locale LANG=en_US.UTF-8
```

---
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> date
# date shows correct TZ, but /etc/localtime and /etc/timezone don't,
# were updated by tzdata update in upgrade
```
***ISSUES:***

5. need to reconfigure tzdata
- > .DEF CHANGES: link localtime, set timezone, noninteractive reconfigure tzdata
```bash
# (in %post)
    ln -snf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
    echo America/Los_Angeles > /etc/timezone
    dpkg-reconfigure --frontend noninteractive tzdata
```

---
### Install firefox browser:
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> apt install firefox-esr
> firefox
# [GFX1-]: glxtest: libpci missing
# [GFX1-]: glxtest: libEGL missing
# firfox GUI starts, but non responsive/window doesn't close
> apt install pciutils libegl-dev
> firefox
> firefox-esr
```
***ISSUES:***
> very slow, but both work - ASK @ZACH WHY SO SLOW??

> ?R? firefox vs firefox-esr

- > .DEF CHANGES: install firefox and dependencies
```bash
    apt update && apt upgrade -y
    apt install -y vim \
        locales \
        firefox-esr pciutils libegl-dev
```

---
### Install xfce desktop:
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> apt install -y xfce4 xfce4-terminal mousepad
> startxfce4
# (process:36851): xfce4-session-CRITICAL **: 02:31:04.470: dbus-launch not found, the desktop will not work properly!
# Segmentation fault
> apt install dbus-x11
> dbus-launch startxfce4
# install VirtualGL
> apt install wget
> wget https://sourceforge.net/projects/virtualgl/files/3.0/virtualgl_3.0_amd64.deb
> dpkg -i virtualgl_3.0_amd64.deb
# virtualgl dependency needed
> apt install libegl1-mesa
> dpkg -i virtualgl_3.0_amd64.deb
> dbus-launch startxfce4
```
***ISSUES:***
ASK @ZACH
> firefox can run from ssh, but not directly on server

> xfce eventually loads from ssh, but errors with display

> xfce immediately lods on server - but is completely unresponsive
> tried giving it a few minutes incase loading in the bkgnd
- > .DEF CHANGES: isntall xfce, dbus, VirtualGL
```bash
# (in %post)
        xfce4 xfce4-terminal mousepad dbus-x11 \
        wget libegl1-mesa
# ...

    # install VirtualGL for xfce
    wget https://sourceforge.net/projects/virtualgl/files/3.0/virtualgl_3.0_amd64.deb
    dpkg -i virtualgl_3.0_amd64.deb
    rm virtualgl_3.0_amd64.deb
```

---
### Install TurboVNC VNC server:
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> wget https://sourceforge.net/projects/turbovnc/files/2.2.7/turbovnc_2.2.7_amd64.deb
> dpkg -i turbovnc_2.2.7_amd64.deb
> rm turbovnc_2.2.7_amd64.deb
> vncserver # not found
> export PATH=/opt/TurboVNC/bin:$PATH
> vncserver
```
---
TEST VNCSERVER:
```
- in container:
```bash
export PATH=/opt/TurboVNC/bin:$PATH
vncserver
```
tunnel VNC through SSH, sends all data through encrypted tunnel. routes packets from localhost (port 5901) to the remote host (port 5901) through port 22
- in a mobaxterm window:
```bash
create vnc session with:
    hostname = localhost
    port = 5901 (5900 + vncserver display #)
    under network settings:
        add ssh gateway with with server ip, user=root, port=22, and key
        password is for vncserver, not server root account
```
> IT WORKS!!!! Responsive GUI desktop!!!
- in container:
```bash
vncserver -list
vncserver -kill :1
```
***ISSUES:***
> have to export TurboVNC to PATH to run vncserver command
---
- > .DEF CHANGES: install TurboVNC, add env section
```bash
%environment
    export PATH=/opt/TurboVNC/bin:$PATH

# (in %post)
    wget https://sourceforge.net/projects/turbovnc/files/2.2.7/turbovnc_2.2.7_amd64.deb
    dpkg -i turbovnc_2.2.7_amd64.deb
    rm turbovnc_2.2.7_amd64.deb
```
---
---

# remote VNC access stage 1: 
## TurboVNC (std VNC server from container to remote VNC client) through ssh tunnel: 
```
VNC Client (localhost:5901) --> SSH Client (remote:22) --]===ssh-tunnel===]--> (192.168.161.131:22) SSH Server --> (localhost:5901) TurboVNC Server
```
```bash
tunnel VNC through SSH, sends all data through encrypted tunnel. 
routes packets from localhost (port 5901) to the remote host (port 5901) through port 22: 
# in container: 
vncserver
# on remote machine: 
ssh -L 5901:localhost:5901 root@192.168.161.131
+ VNC session localhost:5901
```
---
---
### Install NoVNC+websocify
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> apt install -y novnc # installs websocify too
# websocify = WebSockets to TCP socket proxy
> vncserver
> websockify -D --web /usr/share/novnc/ 6080 localhost:5901
# -D flag runs a daemon in bkgd, leave off to see output
```
- in a web browser:
```bash
192.168.161.131:6080/vnc.html
# login with turbovnc password
```
> Can access container through URL!

- in container:
```bash
lsof -i -P -n | grep LISTEN
# look for websockify, process id is first #
kill <pid>
vncserver -list
vncserver -kill :1 # use display num listed above
```

---
- > .DEF CHANGES: isntall novnc+websockify
```bash
# (in %post, apt installs):
        novnc
```
---
---

# remote VNC access stage 2:
## NoVNC + Websockify (HTML-VNC client with websockets served from container, remote user just needs browser to access, not a VNC client):
```
browser :6080/vnc.html --> websocket :6080 --> websockify --> NoVNC :5900 --> TurboVNC Sever
```
```bash
can access container through URL with port
# in container: 
vncserver
websockify -D --web /usr/share/novnc/ 6080 localhost:5901

# on remote machine: 
192.168.161.131:6080/vnc.html
# login with turbovnc password
```
---
---
### Set up container networking
By default, Singularity runs containers in host network namespace:
```bash
singularity shell -w debian
apt install -y iproute2 iputils-ping # for ip command, ping
ip a # same ip as host
# can ssh to host and run container, but need to ssh directly to container
# needs unique ip addr/network namespace
```
 Singularity offers network virtualization --net option to join a new nework ns, but the net flag can only be used by root, need network namespace for unprivledged users.
- create veth pair and network namespace:
```bash
# on host, not in container: create new network namespace with veth to bridge

# create namespace
ip netns add ns0

# create bridge
ip link add br0 type bridge
# assign bridge ip
ip link set br0 up
ip addr add 10.0.123.1/24 dev br0

# create veth pair
ip link add v0-l type veth peer name v0-r
# add v0-l to bridge
ip link set v0-l up
ip link set v0-l master br0
# add v0-r to ns0
ip link set v0-r netns ns0
# assign v0-r (container) ip and default route through bridge
ip netns exec ns0 ip link set lo up
ip netns exec ns0 ip link set v0-r up
ip netns exec ns0 ip addr add 10.0.123.10/24 dev v0-r
ip netns exec ns0 ip route add default via 10.0.123.1

# check
ip a
# on host, not in container:
ping 10.0.123.10     # works, can ping veth ip in ns0 namespace
# run container in network namespace ns0:
ip netns exec ns0 singularity shell -w debian
# in container:
> ip a
> ping 10.0.123.1    # works, can ping veth ip in host namespace
> ping 192.168.161.131  # works, can ping vm host
> ping 8.8.8.8          # doesn't work, can't ping outside of network
> exit

# need to setup ip forwarding and nat
# on host, not in container:
sysctl -w net.ipv4.ip_forward=1
apt install -y iptables
iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
ip netns exec ns0 singularity shell -w debian
# in container:
> ping 8.8.8.8 # works!
> ping google.com # works too!
> exit
```
---
- > .DEF CHANGES:
```bash
# (in %post, apt installs):
        iproute2 iputils-ping
```
---


---
---

# remote VNC access stage 3: 
## NGINX reverse proxy NoVNC+websockify
(see [NGINX Config](../nginx/README.md))
```
browser /mynovnc --> websocket :6080 --> websockify --> NoVNC :5900 --> TurvoVNC Server
```
```bash
can access container through URL without port
# in container: 
vncserver
websockify --web /usr/share/novnc/ 6080 10.0.123.10:5901

# on a remote machine: 
192.168.161.131/mynovnc/vnc.html
```
---
---

# remote VNC access stage 4:
## Websockify with token files
(see [NGINX Config](../nginx/README.md))
```
browser /uniqueURLwithToken --> websocket :6080 --> websockify --> NoVNC :5900 --> TurvoVNC Server
```
```bash
can access container with token (unique URL)
# in container: 
# /usr/local/websockify/token/t1 = "token1: 10.0.123.10:5901
vncserver
websockify --web /usr/share/novnc/ --token-plugin=TokenFile --token-source=/usr/local/websockify/token/t1 6080

# on a remote machine:
http://192.168.161.131/mynovnc/vnc.html?path=/websockify?token=token1
```

---
---

# remote VNC access stage 5:
## Websockify from server with user token files (unique URLs)
(see [NGINX Config](../nginx/README.md))
```
browser /uniqueURLwithToken --> server websocket :6080 --> server websockify --> container NoVNC :5900 --> container TurvoVNC Server
```
```bash
# in container: 
vncserver

# on server, not in container: 
websockify --web /usr/share/novnc/ --token-plugin=TokenFile --token-source=/usr/local/websockify/token/t1 6080

# on a remote machine: 
http://192.168.161.131/index.html
# click link, or use url directly: 
http://192.168.161.131/mynovnc/vnc.html?path=/websockify?token=token1
# vncserver stays running even if exit container shell. 
# can exit shell and still access container vnc!
```
---
---


