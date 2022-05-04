# Server config:

### HANDY COMMANDS:
Clean up history:
```bash
history -w && vim "${HISTFILE}" && history -c && exit
```
---
---
### Install Debian 11 Bullseye in VMWare:
- virtual machine hard disk: 30GB, single file
- create user bmo
- in software selection, uncheck desktop & gnome, keep std system utilities

---
### setup ssh server:
- log in as root, setup up ssh so we can copy/paste rest of config
```bash
apt install -y vim openssh-server
ip a # get VM ip address: 192.168.161.131
```
- I'm using MobaXterm for ssh. To setup key in MobaXterm: 
```
select Tools > MobaKeyGen (MobaXerm SSH Key Generator)
set to Ed25519, select Generate, copy public key, save both keys
paste public key into notepad, save as jc.pub
```
- In PowerShell, copy public key to banyan:
```
cd Desktop
scp jc.pub sskidmore@banyan.engr.unr.edu:~/
```
- From VM, copy keys from banyan to authorized keys file
```
mkdir .ssh
cd .ssh
scp sskidmore@banyan.engr.unr.edu:~/jc.pub .
cat jc.pub >> authorized_keys
```
- In MobaXterm, 
```
create an ssh session with VM ip, user=root, port=22. 
under advanced settings, add private key (.ppk)
```
*can ignore first login error: 
`/usr/bin/xauth:  file /root/.Xauthority does not exist`*

*the file is created at first login, error does not appear at second login.*

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
## Basic NGINX installation and setup: 

### Install nginx:
```bash
apt install -y nginx curl
systemctl status nginx # should be active and running
curl localhost 
# can also check in browser: 
# 192.168.161.131

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
### Create a simple page at localhost/test in /var/www/html: 
```bash
echo "This is a simple NGINX page." >> test.html
```
- add the location to site config file:
```bash
cd /etc/nginx/sites-available
vim default
# under the location / {...} block, add the following and save the file: 
	location /test {
		try_files $uri $uri/ $uri.html =404;
	}
```
- check config file for errors: 
```bash
nginx -t
```
- anytime change a config file - reload nginx to serve the new content:
```bash
systemctl reload nginx
```
- check for new page: 
```bash
curl localhost/test 
# can also check in browser: 
# 192.168.161.131/test
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
## Setup git/github:
### git config:
```bash
git config --list # check for existing git config
# remove global flag to set for cwd
git config --global user.name "Sarah Skidmore"
git config --global user.email "obeytheviszla@gmail.com"
git config --global init.defaultBranch main
# check
git config --list
```
### create ssh key for github:
```bash
ls -al ~/.ssh
# generate ssh key pair
ssh-keygen -t ed25519 -C "obeytheviszla@gmail.com"
# start ssh-agent
eval "$(ssh-agent -s)"
# add key to ssh-agent
ssh-add ~/.ssh/id_ed25519
# copy public key to github settings (in browser)
cat ~/.ssh/id_ed25519.pub
# test SSH connection to GitHub
ssh -T git@github.com
```
### setup project git directories:
```bash
mkdir git && cd git
mkdir canvas && touch canvas/README.md
mkdir config && touch config/README.md
mkdir containers && touch containers/README.md
mkdir nginx && touch nginx/README.md
mkdir systemd && touch systemd/README.md
```
### initialize git branch
```bash
git init
git status
git remote add origin git@github.com:JupyterCanvas/CS426_S22.git
git fetch
git pull origin main
git checkout -b S-rebuild
git add .
git commit -m "Rebuilding VM server, initial commit to set directory structure"
git push --set-upstream origin S-rebuild
```
### Add git branch and status to bash prompt
```bash
vim /etc/bash.bashrc # will apply to all users
```
```bash
parse_git_bg() {
  if [[ $(git status -s 2> /dev/null) ]]; then
    echo -e "\033[0;31m"
  else
    echo -e "\033[0;32m"
  fi
}
# add to PS1 prompt: : \[$(parse_git_bg)\]$(__git_ps1)\[\033[0m\]
# PS1 now:
  PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$\[$(parse_git_bg)\]$(__git_ps1)\[\033[0m\] '
```
---


## Disable xdg default directories generation

There is a utility xdg-user-dirs-update that creates directories when you start an X session: Downloads, Desktop, Videos, etc.. Delete unwanted directories and edit the ~/.config/user-dirs.dirs to suppress:
```bash
# remove Downloads Documents Music Public Templates Videos
rm -r D* M* P* T* V*
# vim ~/.config/user-dirs.dirs 
XDG_DOWNLOAD_DIR="$HOME/"
XDG_DESKTOP_DIR="$HOME/"
XDG_TEMPLATES_DIR="$HOME/"
XDG_PUBLICSHARE_DIR="$HOME/"
XDG_DOCUMENTS_DIR="$HOME/"
XDG_MUSIC_DIR="$HOME/"
XDG_PICTURES_DIR="$HOME/"
XDG_VIDEOS_DIR="$HOME/"
# all paths now just home, no extra directories will be created when log in
# save and run: 
xdg-user-dirs-update
# exit and login again to check 
```
---
