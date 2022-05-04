# add ip forwarding to ns0 namespace
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE

