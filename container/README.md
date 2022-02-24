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
vim /etc/ssh/sshd_config # set PermitRootLogin yes
systemctl restart sshd
systemctl status sshd
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
