#!/bin/sh
# copys important systemd files to local git repo:
cd $(dirname $0)
cp updategit.sh ~/git/uwsgi/
cp apps-available/jupytercan.ini ~/git/uwsgi/apps-available/
