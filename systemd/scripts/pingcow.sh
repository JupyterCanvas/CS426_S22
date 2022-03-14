#!/bin/sh

IP=$(ip a | grep 'inet 10' | awk '{print "ping google.com from ns: "$2" ("$5")"}')
PING=$(ping google.com -c1 | grep 0% | cut -d, -f3)
echo $IP $PING | /usr/games/cowsay
