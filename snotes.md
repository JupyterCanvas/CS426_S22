# 1. re-create virtualenv
NOTES: Fredo had setup virtual environment for Django project with Pipenv. However, per the Pipenv docs: 
```bash
Pipenv is designed to be used by non-privileged OS users. It is not meant to install or handle packages for the whole OS. Running Pipenv as root or with sudo (or Admin on Windows) is highly discouraged and might lead to unintend breakage of your OS.
```
So I am re-creating the virtual environment for the project using virtualenv. 

## Create a virtual environment for project code: 
```bash
apt install python3-pip virtualenv
cd /srv
mkdir apps
cd apps
virtualenv -p python3 venv
```
## Activate virtual environment
```bash
source venv/bin/activate # you can tell you are in the virtual environment b/c of prompt prefix
```
## Install Django in virtual environment
```bash
pip install django
```
## Add Bootstrap to forms with crispy forms
```bash
pip install django-crispy-forms crispy-bootstrap5
```
## Add Python Decouple library for Django secret key storage
```bash
pip install python-decouple
```
## Record venv package lists into requirements.txt
```bash
pip freeze > requirements.txt
```
---

# 2. Rotate Django secret key and setup storage with python decouple
NOTES: We shouldn't have the Django project's secret key visible in version control repo. Since it was previously visible in Fredo's branch (the .env file was included in the repo), I am revoking it, creating a new key, and storing it in the .env file for use. I am also adding the .env file to the project's gitignore file so that it is no longer tracked by git. (Since the key has been rotated, we don't need to remove from previous commits)
```bash
# first, we need to generate a new key. We need a 50 char random string comprised of: 
# a-z, 0-9, and keyboard top-row symbols: !, @, #, $, %, ^, &, *, (, -, _, =, +, and ). 
# This is a one-liner to generate a key on the command line: 
python3 -c 'import random; choice=random.SystemRandom().choice; print("".join([choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for _ in range(50)]));'
```
```bash
# now we need to add the new key to the .env file, 
# I am going to remove the .env file Fredo created at jupytercan/jupytercan 
# and put the new .env file one level up in the root directory of our project. 
mv jupytercan/jupytercan/.env jupytercan/.env
vim jupytercan/.env # add new key
# and add the .env file to a .gitignore file
vim jupytercan/.gitignore # add: .env
```
---

# 4. Check app with runserver (and install firefox for runserver testing)
```bash
./manage.py runserver
```
NOTE: the server doesn't have a graphical user interface for checking the project in a browser. We can initially check with curl:
```bash 
curl localhost:8000/login/
# note - I wonder if something is wrong with the URL mappings? this only works with the exact command above, no response for: 
# curl localhost:8000/login OR curl localhost:8000/ OR curl localhost:8000 ...need to test later
```
While we can see that the server is running with curl, we can install firefox for a GUI. (note that the display may not be exactly as expected, this is for general testing before setting up real server through NGINX, the site is designed to be viewed with Chrome and Firefox may not display correctly, however, I cannot get installation and use of Chrome to work properly, so going with firefox)
```bash
apt install firefox-esr
```
After troubleshooting, I've found the best method for opening firefox is to create a duplicate ssh session for the server in mobaxterm and in the advanced ssh settings tab, add to the execute command field: "firefox about:blank" (no quotes). Preformance is not great, but if it is refusing to load at all, reboot the VM and try again. This is just a temporary option until the site is setup to be served with nginx. 

# 3. Add a superuser to test manually adding users and groups through admin interface
```bash
./manage.py createsuperuser
```

