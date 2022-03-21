#!/bin/sh
# copys important nginx files to local git repo: 
cd $(dirname $0)
cp updategit.sh ~/git/nginx/
cp sites-available/default ~/git/nginx/sites-available/
