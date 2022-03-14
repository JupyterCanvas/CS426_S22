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
## systemd service template to create network namespace
```bash
vim /etc/systemd/system/netns@.service
```
```bash
# Create user network namespaces:
# systemd creates ns, subsequent unprivledged units can join namespace
# subsequent units use NetworkNamespacePath=/var/run/netns/ns%i in [Service] sect

[Unit]
Description=Named network namespace ns%i
Documentation=https://github.com/systemd/systemd/issues/2741#issuecomment-433979748
StopWhenUnneeded=true

[Service]
Type=oneshot
RemainAfterExit=yes

# Ask systemd to create a network namespace
PrivateNetwork=yes

# systemd does not support naming network namespaces
# work around by assigning ip netns namespace name to systemd namespace:

# Ask ip netns to create a named network namespace
# (This ensures that things like /var/run/netns are properly setup)
#ExecStart=/sbin/ip netns add ns%i
# (Why flock? See https://bugs.debian.org/949235
# a race condition in ip netns can result in mount point havoc if ip netns add
# is run for the first time from multiple processes simultaneously)
ExecStart=/usr/bin/flock --no-fork -- /var/run/netns.lock /bin/ip netns add ns%i

# Drop the network namespace that ip netns just created
ExecStart=/bin/umount /var/run/netns/ns%i

# Re-use the same name for the network namespace that systemd put us in
ExecStart=/bin/mount --bind /proc/self/ns/net /var/run/netns/ns%i
```
```bash
systemctl start netns@123.service
systemctl status netns@123.service
```
```bash
● netns@123.service - Named network namespace ns123
     Loaded: loaded (/etc/systemd/system/netns@.service; static)
     Active: inactive (dead)
       Docs: https://github.com/systemd/systemd/issues/2741#issuecomment-433979748

Mar 13 22:05:02 jupytercanvas systemd[1]: Starting Named network namespace ns123...
Mar 13 22:05:02 jupytercanvas systemd[1]: Finished Named network namespace ns123.
Mar 13 22:05:02 jupytercanvas systemd[1]: netns@123.service: Succeeded.
Mar 13 22:05:02 jupytercanvas systemd[1]: Stopped Named network namespace ns123.
```
```bash
ip netns list
# ns123
```
---
## systemd service template to setup networking in network namespaces
```bash
vim /etc/systemd/system/nsbr@.service
```
```bash
[Unit]
Description=Network namespace ns%i configuration
Documentation=https://github.com/systemd/systemd/issues/2741#issuecomment-433979748
StopWhenUnneeded=true

[Service]
Type=oneshot
RemainAfterExit=yes
EnvironmentFile=/etc/systemd/system/netns/ns%i.conf

# setup networking in ns: bridge <- veth -> container
ExecStart=/etc/systemd/system/scripts/netns.sh ns%i vl-%i vr-%i ${VR_IP} ${BR} ${BR_IP}
```
```bash
sytemctl start nsbr@12310.service
sytemctl status nsbr@12310.service
```
```bash
● nsbr@12310.service - Network namespace ns12310 configuration
     Loaded: loaded (/etc/systemd/system/nsbr@.service; static)
     Active: inactive (dead)
       Docs: https://github.com/systemd/systemd/issues/2741#issuecomment-433979748

Mar 13 22:30:12 jupytercanvas systemd[1]: Starting Network namespace ns12310 configuration...
Mar 13 22:30:12 jupytercanvas systemd[1]: Finished Network namespace ns12310 configuration.
Mar 13 22:30:12 jupytercanvas systemd[1]: nsbr@12310.service: Succeeded.
Mar 13 22:30:12 jupytercanvas systemd[1]: Stopped Network namespace ns12310 configuration.
```
```bash
ping 10.0.123.10 # can ping namespace (connection from server to namespace)
ip netns exec ns12310 ping google.com # can ping google from namespace (ip forwarding, internet acces)
```
---
## systemd service template to test networking in namespaces
```bash
vim /etc/systemd/system/testnetns@.service
```
```bash
[Unit]
Description=Test service template join netns

[Service]
NetworkNamespacePath=/var/run/netns/ns%i
# Service now running inside the ns%i named network namespace

# pings google.com from inside container to test network config
ExecStart=/etc/systemd/system/scripts/pingcow.sh
```
```bash
systemctl start testnetns@12310.service
systemctl status testnetns@12310.service
```
```bash
● testnetns@12310.service - Test service template join netns
     Loaded: loaded (/etc/systemd/system/testnetns@.service; static)
     Active: inactive (dead)

Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:  _________________________________________
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]: / ping google.com from ns: 10.0.123.10/24 \
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]: \ (vr-12310) 0% packet loss               /
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:  -----------------------------------------
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:         \   ^__^
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:          \  (oo)\_______
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:             (__)\       )\/\
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:                 ||----w |
Mar 13 23:22:51 jupytercanvas pingcow.sh[132939]:                 ||     ||
Mar 13 23:22:51 jupytercanvas systemd[1]: testnetns@12310.service: Succeeded.
```
---

