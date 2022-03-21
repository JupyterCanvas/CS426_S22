#!/bin/sh
# copys important systemd files to local git repo:
cd $(dirname $0)
cp updategit.sh ~/git/systemd/
cp cont@.service ~/git/systemd/
cp testcont@.service ~/git/systemd/
cp vnc@.service ~/git/systemd/
cp -r scripts/ ~/git/systemd/
cp -r containers/ ~/git/systemd/
cp -r archive/ ~/git/systemd/
