#!/bin/bash

# ./fixvnc.sh username

TASKS=$(systemctl status vnc@${1}.service | grep Tasks: | awk '{print $2}')

echo $TASKS

if [ $TASKS -lt 50 ]
then
    systemctl stop vnc@${1}.service
    systemctl start vnc@${1}.service
fi

sleep 1

TASKS=$(systemctl status vnc@${1}.service | grep Tasks: | awk '{print $2}')

echo $TASKS
