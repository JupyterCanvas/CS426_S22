#!/bin/sh
# removes namespace and bridge created with ns_create.sh

ip link del br0
ip link del v0-l 
ip netns delete ns0
