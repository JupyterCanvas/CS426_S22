#!/bin/bash

echo "created by user from server" >> /home/$1/testuser$1.txt
chown $1:$1 /home/$1/testuser$1.txt
echo "created by real server root from server" >> /home/$1/testrealroot$1.txt
ls /home/$1 | grep test
# add vncserver patch to home dir
cp vncserver /home/$1/
chown $1:$1 /home/$1/vncserver
# add micromamba and nb_canvas initialization script to home dir
cp nbcanvas_init.sh /home/$1/
chown $1:$1 /home/$1/nbcanvas_init.sh
