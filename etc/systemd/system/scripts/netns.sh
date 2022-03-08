#!/bin/sh

# $1 = ns_name nsXXXxx     ns12310
# $2 = vl_name vl-XXXxx    vl-12310
# $3 = vr_name vr-XXXxx    vr-12310
# $4 = vr_ip   10.0.X.x/24 10.0.123.10/24
# $5 = br_name brXXX       br123
# $6 = br_ip   10.0.X.1    10.0.123.1

# create veth pair
ip link add $2 type veth peer name $3
# add vl to bridge
ip link set $2 master $5
ip link set $2 up
# add vr to ns
ip link set $3 netns $1
# assign vr (container) ip and default route through bridge
ip netns exec $1 ip link set lo up
ip netns exec $1 ip link set $3 up
ip netns exec $1 ip addr add $4 dev $3
ip netns exec $1 ip route add default via $6

