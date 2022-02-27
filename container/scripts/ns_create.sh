#!/bin/sh
# creates network ns0 with veth to host

# create veth pair
ip link add v0-l type veth peer name v0-r
# create namespace
ip netns add ns0
# move v0-r to ns0 namespace
ip link set v0-r netns ns0
# set ip for v0-l
ip link set v0-l up
ip addr add 192.168.100.1/24 dev v0-l
# in ns0 namespace, set up v0-r
ip netns exec ns0 ip link set lo up
ip netns exec ns0 ip link set v0-r up
ip netns exec ns0 ip addr add 192.168.100.10/24 dev v0-r
ip netns exec ns0 ip route add default via 192.168.100.1
# test
ip addr show dev v0-l
ip netns exec ns0 ip addr show dev v0-r
ping -c2 192.168.100.10
ip netns exec ns0 ping -c2 192.168.100.1
