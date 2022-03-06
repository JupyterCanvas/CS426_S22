#!/bin/sh

# $1 = br_name = br0 -> "br-" + course
# $2 = br_ip = 10.0.123.1/24 = 10.0.x.1/24 w/ x = course num = 123 = 10.0.123.1/24

# create bridge
ip link add $1 type bridge
# assign bridge ip
ip link set $1 up
ip addr add $2 dev $1

