#!/bin/bash

mkdir /root/.vnc
/opt/TurboVNC/bin/vncpasswd -f <<< qwerty > /root/.vnc/passwd
chmod -R 600 /root/.vnc/passwd

