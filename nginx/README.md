# NGINX Config
---

## Basic NGINX installation and setup: 

### Install nginx:
```bash
apt install -y nginx curl
systemctl status nginx # should be active and running
curl localhost 
# can also check in browser: 
# 192.168.161.131

# these are the nginx config files:
cd /etc/nginx && ls
    # main server config file: /etc/nginx/nginx.conf
    # all sites config files: /etc/nginx/sites-available
    # simlinks to available so easy to turn sites on/off: /etc/nginx/sites-enabled
    # /etc/nginx/sites-enabled/default -> /etc/nginx/sites-available/default

# these are the html files used by nginx
cd /var/www/html && ls
    # index.nginx-debian.html is the default page
```
### Create a simple page at localhost/test in /var/www/html: 
```bash
echo "This is a simple NGINX page." >> test.html
```
- add the location to site config file:
```bash
cd /etc/nginx/sites-available
vim default
# under the location / {...} block, add the following and save the file: 
	location /test {
		try_files $uri $uri/ $uri.html =404;
	}
```
- check config file for errors: 
```bash
nginx -t
```
- anytime change a config file - reload nginx to serve the new content:
```bash
systemctl reload nginx
```
- check for new page: 
```bash
curl localhost/test 
# can also check in browser: 
# 192.168.161.131/test
```
---

### Setup basic reverse proxy with NGINX
```bash
# on server, not in container: 

vim /etc/nginx/sites-available/default
# setup NoVNC to be served through http://ip.of.server/mynovnc/vnc.html
# Reverse proxy NoVNC+websockify:
# adapted from https://github.com/novnc/noVNC/wiki/Proxying-with-nginx
```
```bash
        # path to URL where it will be viewed (http://192.168.161.139/mynovnc/vnc.html)
        location /mynovnc {
                proxy_pass http://10.0.100.10:6080/;
        }

        # path to /websockify to proxy the websocket connection
        location /websockify {
                proxy_http_version 1.1;
                proxy_pass http://10.0.123.10:6080/;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";

                # VNC connection timeout
                proxy_read_timeout 61s;

                # Disable cache
                proxy_buffering off;
        }
```
check config and reload nginx:
```bash
nginx -t
systemctl reload nginx
```
test: 
```bash
ip netns exec ns0 singularity shell -w debian
# in container: 
> vncserver
> websockify --web /usr/share/novnc/ 6080 10.0.123.10:5901
```
in a browser: 
```
192.168.161.131/mynovnc/vnc.html
```
```bash
# in container: 
> CTRL-C
> vncserver -kill :1
> exit
```
***ISSUES:***
> "/websockify" location needed by novnc, can't prepend or append to path. When can't access it get error, cannot connect to ws://192.168.161.131/websockify Need to find another way to proxy pass outside of websockify location or how to change path used by novnc??? 
---

---
### Websockify with token files
```bash
# in container, start websockify server with token instead of ip:port
ip netns exec ns0 singularity shell -w debian
mkdir -p /usr/local/websockify/token/
vim /usr/local/websockify/token/t1
# add the following to file: 
token1: 10.0.123.10:5901
vncserver
websockify --web /usr/share/novnc/ --token-plugin=TokenFile --token-source=/usr/local/websockify/token/t1 6080
```
in a browser: 
```bash
http://192.168.161.131/mynovnc/vnc.html?path=/websockify?token=token1
```
***ISSUES:***
> still running a distinct websockify instance in user containers, need to change nginx config and run single websockify instance on server that responds to user html requests
---
