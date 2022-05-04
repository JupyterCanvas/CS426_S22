#!/bin/sh
#./killws.sh wsport#
#./killws.sh 6081

# set port to kil and
# find websockify processes
# pass port to kill to awk and find pid
# pass pid to kill (-r: if found)

WSPORT=$1 && 
	ps aux | 
	grep websockify | 
	awk -v wsp=$WSPORT '{pid=$2; wsport=$18; if (wsp == wsport) print pid}' | 
	xargs -r kill

