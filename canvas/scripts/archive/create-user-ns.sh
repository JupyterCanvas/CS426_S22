#!/bin/sh

# $1 = ns_name = ns0 -> "ns-" + user
# $2 = veth-l_name = "vl-" + user (-> br)
# $3 = veth-r_name = "vr-" + user (-> ns)
# $4 = veth-r ip = 10.0.123.x/24 w/ x = 10-254 = 10.0.123.10/24
# $5 = br_name = br0 -> "br-" + course
# $6 = br ip = 10.0.x.1/24 = 10.0.123.1/24

# create namespace
ip netns add $1
# create veth pair
ip link add $2 type veth peer name $3
# add v0-l to bridge
ip link set $2 up
ip link set $2 master $5
# add v0-r to ns0
ip link set $3 netns $1
# assign v0-r (container) ip and default route through bridge
ip netns exec $1 ip link set lo up
ip netns exec $1 ip link set $3 up
ip netns exec $1 ip addr add $4 dev $3
ip netns exec $1 ip route add default via $6

