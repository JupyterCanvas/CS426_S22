#!/bin/sh
# removes namespace and bridge created with ns_create.sh

ip link del br0
ip netns delete ns0
