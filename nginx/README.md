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

