#!/bin/bash

echo "created by user from server" >> /home/$1/testuser$1.txt
chown $1:$1 /home/$1/testuser$1.txt
echo "created by real server root from server" >> /home/$1/testrealroot$1.txt
ls /home/$1 | grep test

