
# Systemd config

### Allow process running as an unprivileged user to use a private network namespace

- Unprivledged users can not use ip netns exec when starting container. 

- Let systemd create the namespace, subsequent units join namespace and subsequent joins can be unprivledged. 

- Use systemd template units and EnvironmentFiles to create unit instances
---

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
- systemd does not support named network interfaces. Combine with ip netns namespaces to work around (source https://github.com/systemd/systemd/issues/2741#issuecomment-433979748)

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

## Link instance service dependencies: 

- Use systemd BindTo+After in testnetns and nsbr services to link instance dependencies: 
```bash
vim /etc/systemd/system/nsbr@.service
```
```bash
# in [Unit]
# Ensure namespace configured
BindsTo=netns@%i.service
After=netns@%i.service
```
```bash
vim /etc/systemd/system/testnetns@.service
```
```bash
# in [Unit]
# Ensure network is configured
BindsTo=nsbr@%i.service
After=nsbr@%i.service
```
```bash
ip netns delete ns12310
systemctl start testnetns@12310.service
systemctl status testnetns@12310.service
```
```bash
● testnetns@12310.service - Test service template join netns
     Loaded: loaded (/etc/systemd/system/testnetns@.service; static)
     Active: inactive (dead)

Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:  _________________________________________
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]: / ping google.com from ns: 10.0.123.10/24 \
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]: \ (vr-12310) 0% packet loss               /
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:  -----------------------------------------
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:         \   ^__^
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:          \  (oo)\_______
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:             (__)\       )\/\
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:                 ||----w |
Mar 14 00:01:08 jupytercanvas pingcow.sh[133844]:                 ||     ||
Mar 14 00:01:08 jupytercanvas systemd[1]: testnetns@12310.service: Succeeded.
```
`systemctl start testnetns@12310.service` starts: 
- an instance of the testnetns service, 
- it also creates a nsbr@12310.service instance, 
- which creates a netns@12310.service instance. 
- only call the sub unit service and its dependencies are generated automatically.
```bash
root@jupytercanvas:/etc/systemd/system# systemctl status nsbr@12310.service
● nsbr@12310.service - Network namespace ns12310 configuration
     Loaded: loaded (/etc/systemd/system/nsbr@.service; static)
     Active: inactive (dead)
       Docs: https://github.com/systemd/systemd/issues/2741#issuecomment-433979748

Mar 14 00:01:08 jupytercanvas systemd[1]: Starting Network namespace ns12310 configuration...
Mar 14 00:01:08 jupytercanvas systemd[1]: Finished Network namespace ns12310 configuration.
Mar 14 00:01:08 jupytercanvas systemd[1]: nsbr@12310.service: Succeeded.
Mar 14 00:01:08 jupytercanvas systemd[1]: Stopped Network namespace ns12310 configuration.
```
```bash
root@jupytercanvas:/etc/systemd/system# systemctl status netns@12310.service
● netns@12310.service - Named network namespace ns12310
     Loaded: loaded (/etc/systemd/system/netns@.service; static)
     Active: inactive (dead)
       Docs: https://github.com/systemd/systemd/issues/2741#issuecomment-433979748

Mar 14 00:01:07 jupytercanvas systemd[1]: Starting Named network namespace ns12310...
Mar 14 00:01:08 jupytercanvas systemd[1]: Finished Named network namespace ns12310.
Mar 14 00:01:08 jupytercanvas systemd[1]: netns@12310.service: Succeeded.
Mar 14 00:01:08 jupytercanvas systemd[1]: Stopped Named network namespace ns12310.
```
**The network bridge is not part of the dependency stack. Run the bridge service before the netns services. (systemtl start netbr@123.service)**

Cleanup: Removing the network namespace also removes the veth pair
    
`ip netns list`
    
`ip netns delete ns12310`

---
## simple systemd service template to generate a container instance from an image

- Can't access systemd inside of container (for systemctl restart jupyter) 
- Can run services such as vncserver or jupyter, but won't be able to manage them (become orphans)
### To run services in a SingularityCE container, use instances that run in the background: 
```bash
vim /etc/systemd/system/cont@.service
```
```bash
[Unit]
Description=Generate container instance

[Service]
# forking because 'instance start' starts an instance and exits
Type=forking
# consider the unit to be active if the start action exited successfully
RemainAfterExit=yes

# start singularity instance
ExecStart=/usr/local/bin/singularity instance start /data/containers/alpine_latest.sif inst-%i

# stop singularity instance
ExecStop=/usr/local/bin/singularity instance stop inst-%i
```
```bash
# start instance 
systemctl start cont@test123.service
# check
systemctl status cont@test123.service
singularity instance list
singularity shell instance://inst-test123
cat /etc/os-release
# stop instance
systemctl stop cont@test123.service
# check
singularity instance list
systemctl status cont@test123.service
```
---
## generate a container instance as an unprivledged user

- Add user to container service template: 
```bash
vim /etc/systemd/system/cont@.service
```
```bash
# in [Service] section: 
User=cs123-newellz2
```
```bash
# reload config
systemctl daemon-reload
systemctl start cont@123.service
systemctl status cont@123.service
# Instances started by another user won't be listed when singularity list called by root:
singularity instance list # no results
# Instances are linked with the user account that started them:
su cs123-newellz2
singularity instance list # shows inst-123 instance
singularity shell instance://inst-123
whoami 
exit # from container
exit # from user (back to root)
```
---
## generate container instance as user in user network namespace

```bash
vim /etc/systemd/system/cont@.service
```
```bash
# in [Service] section before ExecStart of singularity instance: 
NetworkNamespacePath=/var/run/netns/ns%i
# Service now running inside the ns%i named network namespace
```
```bash
systemctl daemon-reload
systemctl start cont@12310.service
systemctl status cont@12310.service
# Instances are linked with the user account that started them:
su cs123-newellz2
singularity instance list # shows inst-12310 instance
singularity shell instance://inst-12310
ip a # shows 10.0.123.10 ip of network namespace
exit # from container
exit # from user (back to root)
```
---

