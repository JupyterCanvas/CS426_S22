#!/bin/bash

# run nbcanvas initialization script to create
# course directory and nbgrader config within container
sudo -u $1 singularity exec instance://inst-$1 /root/nbcanvas_init.sh

