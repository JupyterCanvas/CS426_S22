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

