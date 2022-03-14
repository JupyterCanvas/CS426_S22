# Systemd config

## Simple service example.service
```bash
apt install cowsay
PATH=$PATH:/usr/games
```
```bash
vim /etc/systemd/system/example.service
```
```bash
[Unit]
Description=a simple service

[Service]
Type=simple
ExecStart=/etc/systemd/system/scripts/time.sh

[Install]
WantedBy=multi-user.target
```
```bash
vim /etc/systemd/system/scripts/time.sh
```
```bash
#!/bin/sh

echo $(date) | /usr/games/cowsay
```
```bash
systemctl start example.service
systemctl status example.service
```
```bash
● example.service - a simple service
     Loaded: loaded (/etc/systemd/system/example.service; disabled; vendor preset: enabled)
     Active: inactive (dead)

Mar 13 21:17:26 jupytercanvas systemd[1]: Started a simple service.
Mar 13 21:17:26 jupytercanvas time.sh[129284]:  _________________________________
Mar 13 21:17:26 jupytercanvas time.sh[129284]: < Sun 13 Mar 2022 09:17:26 PM PDT >
Mar 13 21:17:26 jupytercanvas time.sh[129284]:  ---------------------------------
Mar 13 21:17:26 jupytercanvas time.sh[129284]:         \   ^__^
Mar 13 21:17:26 jupytercanvas time.sh[129284]:          \  (oo)\_______
Mar 13 21:17:26 jupytercanvas time.sh[129284]:             (__)\       )\/\
Mar 13 21:17:26 jupytercanvas time.sh[129284]:                 ||----w |
Mar 13 21:17:26 jupytercanvas time.sh[129284]:                 ||     ||
Mar 13 21:17:26 jupytercanvas systemd[1]: example.service: Succeeded.
```
---
## systemd service template to launch course bridge instances 
```bash
vim /etc/systemd/system/netbr@.service
```
```bash
[Unit]
Description=Network bridge br-%i
StopWhenUnneeded=true

[Service]
Type=oneshot
RemainAfterExit=yes
# netns/123/bridge-123.conf stores ip:
# BR_IP=10.0.123.1
EnvironmentFile=/etc/systemd/system/netns/%i/bridge-%i.conf

# create bridge
ExecStart=/sbin/ip link add br-%i type bridge

# assign bridge ip
ExecStart=/sbin/ip link set br-%i  up
ExecStart=/sbin/ip addr add ${BR_IP} dev br-%i

[Install]
WantedBy=multi-user.target
```

```bash
mkdir -p netns/123/ 
vim netns/123/bridge-123.conf
```
```bash
BR_IP=10.0.123.1
```
```bash
systemctl start netbr@123.service
systemctl status netbr@123.service
```
```bash
● netbr@123.service - Network bridge br-123
     Loaded: loaded (/etc/systemd/system/netbr@.service; disabled; vendor preset: enabled)
     Active: inactive (dead)

Mar 13 21:46:51 jupytercanvas systemd[1]: Starting Network bridge br-123...
Mar 13 21:46:51 jupytercanvas systemd[1]: Finished Network bridge br-123.
Mar 13 21:46:51 jupytercanvas systemd[1]: netbr@123.service: Succeeded.
Mar 13 21:46:51 jupytercanvas systemd[1]: Stopped Network bridge br-123.
```
---

