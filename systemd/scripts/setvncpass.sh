#!/bin/sh
#./setvncpass.sh username vncserverport#

sudo -u $1 singularity exec instance://inst-$1 mkdir /root/.vnc
sudo -u $1 singularity exec instance://inst-$1 bash -c "/opt/TurboVNC/bin/vncpasswd -f <<< qwerty > /root/.vnc/passwd"
sudo -u $1 singularity exec instance://inst-$1 chmod -R 600 /root/.vnc/passwd
sudo -u $1 singularity exec instance://inst-$1 /opt/TurboVNC/bin/vncserver :$2

