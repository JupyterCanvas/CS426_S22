#!/bin/bash

# sets up and activates micromamba virtualenv, gets nb_canvas repo

cd /root

# download micromamba
wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj bin/micromamba

# setup and source environment
./bin/micromamba shell init -s bash -p ~/micromamba
source ~/.bashrc

# create and activate virtualenv
micromamba create -n jupyter-canvas
micromamba activate jupyter-canvas

# installs and configs
micromamba install -y xeus-cling dotnet-interactive pip -c conda-forge
pip install jupyterlab nbgrader canvasapi nose nbclient==0.5.11 jupyter-server==1.12.0 jupyter-client==6.1.12 traitlets==4.3.3 nbconvert==5.6.1 jupyter-console==6.4.2 jinja2==3.0.3
jupyter nbextension install --sys-prefix --py nbgrader --overwrite
jupyter nbextension enable --sys-prefix --py nbgrader
jupyter serverextension enable --sys-prefix --py nbgrader

# get Zach's nb_canvas repo
git clone https://github.com/zachestreito/nb_canvas
cd nb_canvas
git update-index --assume-unchanged config.ini

# after this script, a couple more steps: 
echo "next: \t get API key, update config.ini:"
echo " \t API_URL = https://webcampus.unr.edu"
echo " \t API_KEY = [replace with key]"
echo " \t COURSE_ID = 83090"
echo " \t COURSE_DIRECTORY = ~/examplecourse10/"
echo "then: \t python3 nb_canvas.py # sets up nbgrader and course dir"
