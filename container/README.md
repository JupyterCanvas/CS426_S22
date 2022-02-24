# Container configuration notes
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
