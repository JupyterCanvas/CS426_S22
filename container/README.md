
# Container configuration notes
---
[Server Config](#server-config)

[Singularity Container Config](#singularity-container-config)

---
---
# Singularity container config:

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
standard development cycle (Singularity flow):
> 1. create a writable container (sandbox)
> 2. shell into container with --writable option and tinker with it interactively
> 3. record changes in definition file
> 4. rebuild the container from the definition file prn
> 5. rinse and repeat until we are happy with result
> 6. rebuild the container from the final definition file as a read-only singularity image format (SIF) image for use in production
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
- in container:
```bash
export PATH=/opt/TurboVNC/bin:$PATH
vncserver
```

- in a powershell window:

tunnel VNC through SSH, sends all data through encrypted tunnel. routes packets from localhost (port 5901) to the remote host (port 5901) through port 22

```bash
ssh -L 5901:localhost:5901 root@192.168.161.139
```
- in a mobaxterm window:
```bash
hostname = localhost
port = 5901
password is for vncserver, not server root account
```
> IT WORKS!!!! Responsive GUI desktop!!!
- in container:
```bash
vncserver -list
vncserver -kill :1
```
---
- > .DEF CHANGES: install TurboVNC, test VNC through SSH tunnel
```bash
# (in %post)
    wget https://sourceforge.net/projects/turbovnc/files/2.2.7/turbovnc_2.2.7_amd64.deb
    dpkg -i turbovnc_2.2.7_amd64.deb
    rm turbovnc_2.2.7_amd64.deb
    export PATH=/opt/TurboVNC/bin:$PATH
```
---
### Install JupyterLab
shell back in:
```bash
singularity shell --writable debian
```
```bash
# in container:
> apt install -y python3-pip
> pip install jupyterlab
# still in container, on mobaxterm
> jupyter lab # running as rot not recommended
> jupyter lab --allow-root
# runs, seems like it doesn't work in browser...
# but just takes a long time to load in browser from mobaxterm ssh (2.5m)
```
TEST WITH VNC:

*[note - see [updated vnc through ssh mobaxterm notes](#ssh-vnc-with-key)]*

- in container:
```bash
export PATH=/opt/TurboVNC/bin:$PATH
vncserver
```
- in powershell window: tunnel VNC through SSH
```bash
ssh -L 5901:localhost:5901 root@192.168.161.139
```
- in mobaxterm window:
```bash
hostname = localhost, port = 5901
password is for vncserver, not server root account
# open desktop terminal
jupyter lab --allow-root
```
> desktop GUI loads quickly AND can open JupyterLab quickly!
- in container:
```bash
vncserver -kill :1
```
***ISSUES:***
ASK @ZACH
> can't run systemctl status jupyter in container. fails with:\
> `Running in chroot, ignoring request.`
---
- > .DEF CHANGES: install pip, jupyterlab, test jupyter with vnc
```bash
# (in %post, apt installs):
        python3-pip

    # install JupyterLab
    pip install jupyterlab
```
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
192.168.161.139:6080/novnc.html
# login with turbovnc password
```
> Can access container through URL!
```bash
# open terminal, launch jupyter lab
jupyter lab --allow-root
# launches, but reports error:
# Could not determine jupyterlab build status without nodejs
# stop jupyter server CTRL-C CTRL-C
apt install -y nodejs npm
jupyter lab --allow-root
# no error, reports: Build is up to date
```
(close browser)
- in container:
```bash
lsof -i -P -n | grep LISTEN
# look for websockify, process id is first #
kill <pid>
vncserver -list
vncserver -kill :1 # use display num listed above
```
***ISSUES:***
> have to export TurboVNC to PATH to run vncserver command
---
- > .DEF CHANGES: isntall novnc+websockify, add env section, fix jupyter lab error
```bash
%environment
    export PATH=/opt/TurboVNC/bin:$PATH

# (in %post, apt installs):
        novnc nodejs npm
```
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
ip addr add 10.0.100.1/24 dev br0

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
ip netns exec ns0 ip addr add 10.0.100.10/24 dev v0-r
ip netns exec ns0 ip route add default via 10.0.100.1

# check 
ip a
# on host, not in container:
ping 10.0.100.10     # works, can ping veth ip in ns0 namespace
# run container in network namespace ns0:
ip netns exec ns0 singularity shell -w debian
# in container:
> ip a
> ping 10.0.100.1    # works, can ping veth ip in host namespace
> ping 192.168.161.139  # works, can ping vm host
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
---
- > .DEF CHANGES:
```bash
# (in %post, apt installs):
        iproute2 iputils-ping
```
---
### Basic nginx installation and setup (on server): 

Install nginx:
```bash
apt install -y nginx curl
systemctl status nginx # should be active and running
curl localhost 

# these are the nginx config files:
cd /etc/nginx && ls
    # main server config file: /etc/nginx/nginx.conf
    # all sites config files: /etc/nginx/sites-available
    # simlinks to available so easy to turn sites on/off: /etc/nginx/sites-enabled
    # /etc/nginx/sites-enabled/default -> /etc/nginx/sites-available/default

# these are the html files used by nginx
cd /var/www/html && ls
    # index.nginx-debian.html is the default page
```
Create a simple page at localhost/test in /var/www/html: 
```bash
echo "This is a simple NGINX page." >> test.html
```
add the location to site config file:
```bash
cd /etc/nginx/sites-available
vim default
# under the location / {...} block, add the following and save the file: 
	location /test {
		try_files $uri $uri/ $uri.html =404;
	}
```
check config file for errors: 
```bash
nginx -t
```
anytime change a config file - reload nginx to serve the new content:
```bash
systemctl reload nginx
```
check for new page: 
```bash
curl localhost/test 
```
---
### Setup basic reverse proxy with NGINX
```bash
# on server, not in container: 

vim /etc/nginx/sites-available/default
# setup NoVNC to be served through http://ip.of.server/mynovnc/vnc.html
# Reverse proxy NoVNC+websockify:
# adapted from https://github.com/novnc/noVNC/wiki/Proxying-with-nginx

        # path to URL where it will be viewed (http://192.168.161.139/mynovnc/vnc.html)
        location /mynovnc {
                proxy_pass http://10.0.100.10:6080/;
        }

        # path to /websockify to proxy the websocket connection
        location /websockify {
                proxy_http_version 1.1;
                proxy_pass http://10.0.100.10:6080/;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";

                # VNC connection timeout
                proxy_read_timeout 61s;

                # Disable cache
                proxy_buffering off;
        }
```
check config and reload nginx:
```bash
nginx -t
systemctl reload nginx
```
test: 
```bash
ip netns exec ns0 singularity shell -w debian
# in container: 
> vncserver
> websockify --web /usr/share/novnc/ 6080 10.0.100.10:5901
```
in a browser: 
```
192.168.161.139/mynovnc/vnc.html
```
```bash
# in container: 
> CTRL-C
> vncserver -kill :1
> exit
```
***ISSUES:***
> "/websockify" location needed by novnc, can't prepend or append to path. When can't access it get error, cannot connect to ws://192.168.161.139/websockify Need to find another way to proxy pass outside of websockify location or how to change path used by novnc??? 
---
### Websockify with token files
```bash
# on server, not in container: 
mkdir -p /usr/local/websockify/token/
vim /usr/local/websockify/token/t1
# add the following to file: 
token1: 10.0.100.10:5901
# start server with token instead of ip:port
ip netns exec ns0 singularity shell -w debian
vncserver
websockify --web /usr/share/novnc/ --token-plugin=TokenFile --token-source=/usr/local/websockify/token/t1 6080
```
in a browser: 
```bash
http://192.168.161.139/mynovnc/vnc.html?path=/websockify?token=token1
```
***ISSUES:***
> still running a distinct websockify instance in user containers, need to change nginx config and run single websockify instance on server that responds to user html requests
---


---
---


# Server config:

### HANDY COMMANDS:
Clean up history:
```bash
history -w && vim "${HISTFILE}" && history -c && exit
```
---
---
### Install Debian 11 Bullseye in VMWare:
create user bmo

in software selection, uncheck desktop & gnome, keep std system utilities

---
### setup ssh server:
```bash
apt install -y vim openssh-server
```
~~vim /etc/ssh/sshd_config # set PermitRootLogin yes~~
update: shouldn't allow root login with password, can be bruteforced; use keys instead.
see [updated ssh through mobaxterm notes](#ssh-vnc-with-key)
```bash
ip a
```

---
### setup bash history:
```bash
vim .bashrc
```
```bash
# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=10000000
HISTFILESIZE=20000000

#PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"
# if don't wan't commands from other terminals in up arrow history:
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"
```
```bash
source .bashrc
```

---
### Install sudo, add user bmo to sudo group:
```bash
apt install -y sudo
usermod -aG sudo bmo
```

---
### Install manpages:
```bash
apt install -y man manpages manpages-dev info groff
mandb
```

---
## SingularityCE 3.9 Installation from Source:
see: https://sylabs.io/guides/3.9/admin-guide/admin_quickstart.html

### Install dependencies:
```bash
apt install -y build-essential uuid-dev libgpgme-dev squashfs-tools libseccomp-dev wget pkg-config git cryptsetup-bin debootstrap
```

### Install Go:
```bash
dpkg --print-architecture
# amd64
```

### Download Go package archive see: https://go.dev/dl/
```bash
export VERSION=1.17.7 OS=linux ARCH=amd64
wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz
tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz
rm go1.17.7.linux-amd64.tar.gz
```

### Set up environment for Go:
```bash
echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc && source ~/.bashrc
```

### Download SingularityCE from a Github release:
```
export VERSION=3.9.5
wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz
tar -xzf singularity-ce-${VERSION}.tar.gz
rm singularity-ce-3.9.5.tar.gz
```

### Compile and Install SingularityCE:
```bash
cd singularity-ce-3.9.5/
./mconfig && make -C ./builddir && make -C ./builddir install
```

---
---
### ssh vnc with key

*using ssh key with tunnel for vnc in mobaxterm*

1. In mobaxterm, select Tools > MobaKeyGen (MobaXerm SSH Key Generator)
```
set to Ed25519, select Generate, save public and private keys
```
2. add public key to the VM's /root/.ssh/authorized_keys file

**for ssh to VM in mobaxterm:** create ssh session with ip, user=root, port=22. under advanced settings, add private key (.ppk)

**for vnc tunnel through ssh:** create vnc session with ip=localhost, port=5901 (5900 + vncserver display #). under network settings, add ssh gateway with with ip, user=root, port=22, and key.

