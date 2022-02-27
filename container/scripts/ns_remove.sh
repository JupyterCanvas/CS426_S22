#!/bin/sh
# removes ns0 and veth created with ns_create.sh

ip link del v0-l
ip netns delete ns0
