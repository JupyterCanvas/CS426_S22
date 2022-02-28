#!/bin/sh
# creates network ns0 with veth to bridge

# create namespace
ip netns add ns0

# create bridge
ip link add br0 type bridge
# assign bridge ip
ip link set br0 up
ip addr add 10.0.100.1/24 dev br0

# create veth pair
ip link add v0-l type veth peer name v0-r
# add v0-l to bridge
ip link set v0-l up
ip link set v0-l master br0
# add v0-r to ns0
ip link set v0-r netns ns0
# assign v0-r (container) ip and default route through bridge
ip netns exec ns0 ip link set lo up
ip netns exec ns0 ip link set v0-r up
ip netns exec ns0 ip addr add 10.0.100.10/24 dev v0-r
ip netns exec ns0 ip route add default via 10.0.100.1

# start container shell with: 
# ip netns exec ns0 singularity shell -w debian

