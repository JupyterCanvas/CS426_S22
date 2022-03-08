#!/bin/sh

iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE

