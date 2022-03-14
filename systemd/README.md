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

