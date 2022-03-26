#!/bin/bash
# ./fixvnc.sh username
# stops/starts vnc service to fix vncserver bug
# can still be run on individual users, no longer called in create script
# bug fixed with vncserver executable patch

# if service is stopped, grep won't find "Tasks:", check return code: 
status=$(systemctl status vnc@${1}.service | grep "Tasks:" | echo $?)
if [ $status -eq 0 ]
then
    # wrap response in $(( + 0 )) to convert to integer
    TASKS=$(($(systemctl status vnc@${1}.service | grep "Tasks:" | awk '{print $2}') + 0))
else
    # set default value if service stopped
    TASKS=0
fi

# if less than 50 tasks, service did not fully start, stop and start again
if [ $TASKS -lt 50 ]
then
    systemctl stop vnc@${1}.service
    sleep 5
    systemctl start vnc@${1}.service
    # if check status immediately after start only ~9 tasks, let service fully start before check:
    sleep 7
    TASKS=$(systemctl status vnc@${1}.service | grep Tasks: | awk '{print $2}')

    # if still less than 50 tasks, alert admin to check status
    if [ $TASKS -lt 50 ] 
    then
        echo -e "check the service for $1:\n\t'systemctl status vnc@$1.service'\n\t(reload the service with './fixvnc.sh $1')"
	exit 1
    else
        echo "vnc service for $1 started successfully"
    fi

# if service status reports more than 50 tasks, was fully started:     
else
   echo "vnc service for $1 started successfully"
   exit 0
fi
