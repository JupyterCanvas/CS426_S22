#!/bin/sh
# copys singularity config files to local git repo: 
cd $(dirname $0)
cp updategit.sh /root/git/systemd/usr/local/etc/singularity/
cp singularity.conf /root/git/systemd/usr/local/etc/singularity/
cp network/01_contbridge.conflist /root/git/systemd/usr/local/etc/singularity/network/
