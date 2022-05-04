#!/bin/sh
#./pingcow.sh username

USER=$(sudo -u $1 singularity exec instance://inst-$1 whoami)
# USER = root
USERST=$(echo $1 is $USER in container)
# USERST = cs123-newellz2 is root in container 
IP=$(sudo -u $1 singularity exec instance://inst-$1 ip a | grep 'inet 10' | awk '{print "ping google.com from container ip ("$2"): "}')
# IP = ping google.com from container ip (10.0.123.10/24): 
PING=$(sudo -u $1 singularity exec instance://inst-$1 ping google.com -c1 | grep 0% | cut -d, -f3)
# PING = 0% packet loss

echo $USERST $IP $PING | /usr/games/cowsay

# _____________________________________
#/ cs123-newellz2 is root in container \
#| ping google.com from container ip   |
#\ (10.0.123.10/24): 0% packet loss    /
# -------------------------------------
#        \   ^__^
#         \  (oo)\_______
#            (__)\       )\/\
#                ||----w |
#                ||     ||

