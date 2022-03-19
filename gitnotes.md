# Add git branch and status to bash prompt
```bash
# add the following to /etc/bash.basrc (will apply to all users)
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


# Git/Github setup: 
```bash
git config --list # check for existing git config
# remove global flag to set for cwd
git config --global user.name "Sarah Skidmore"
git config --global user.email "obeytheviszla@gmail.com"
git config --global init.defaultBranch main
# check
git config --list
```
## check for ssh key
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
## initialize git 
```bash
mkdir test
cd test
git init
# check
git status
git remote add origin git@github.com:JupyterCanvas/CS426_S22.git
git fetch
git pull origin main
git status
```
## Setting up a new personal development branch
```bash
# There are a lot of unecessary steps here especially all the calls to git status
# but using lots status checks and things like fetch before pull to get a better understanding of process:

# make sure local is up to date with remote before create branch
git status
# see if anything updated on remote repo 
git fetch
git status
# merge updates from remote with local git
git pull
git status
```
## create a new branch
```bash
# -b option creates the branch if it does not exist and switches to it
# command is git checkout -b nameOfNewBranchHere, I am using the name "main-S" ("main-{my first initial}")
git checkout -b test-git

# check using new branch
git status
```
```bash
# create a test file and push to new branch
mkdir testgit
cd testgit
vim testgit.txt
git status
git add .
git status
git commit -m "testing gitnotes"
git push --set-upstream origin test-git

# note, after setting the upstream branch, can just use git push for subsequent commits to branch
# edit testgit.txt
vim testgit.txt
git status
git add .
git status
git commit -m "testing gitnotes: subsequent push to branch after upstream set"
git push
```
```bash
# (optional) pulling from main to branch
# Example: updated repo README in main and merged updated main with my branch
# switch to main branch to update repo README
cd ..
git checkout main
git status

# add a new file to main branch
vim testgit.txt
git status
git add .
git status
git commit -m "testing gitnotes: pulling from branch to main"

# push to main branch
# since we have been working in different branch, be sure to set upstream with -u option
git push -u origin main
git status

# switch back to personal development branch
git checkout test-git
git status
# pull updates from main branch into local development branch
git fetch origin main
git pull origin main
git status
# push updates to development branch to remote 
git push -u origin test-git
git status
# have now merged updates from main branch into personal development branch
# does not modify/update main branch in any way
```
