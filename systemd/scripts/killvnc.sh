#!/bin/sh
#./killvnc.sh username 

# list vncserver instances running in container
# if find running instance, kill it
# assumes single display to kill - only kills last instance in list (the highest number active display)

sudo -u $1 singularity exec instance://inst-$1 vncserver -list | 
       	awk 'END{vp=$1; if (vp != "X") print vp}' |
	xargs -r sudo -u $1 singularity exec instance://inst-$1 vncserver -kill $2
	#xargs -r echo "found it: $1,$2"


