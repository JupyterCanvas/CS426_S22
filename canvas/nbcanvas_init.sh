#!/bin/bash

# make sure in home dir, /root
cd && pwd
# create micromamba envs dir and simlink
mkdir -p micromamba/envs
ln -s /opt/micromamba/envs/* micromamba/envs/
# source the micromamba script
eval "$(/opt/bin/micromamba shell hook --shell=bash)"
# activate the virtual environment (to initialize nbgrader)
micromamba activate jupyter-canvas

# now in (jupyter-canvas) environment

# create nb_canvas dir and simlink
mkdir nb_canvas
ln -s /opt/nb_canvas/* nb_canvas/
# run nb_canvas library initialization script
cd nb_canvas/ 
python3 nb_canvas.py

# creates /root/examplecourse11/ and nbgrader config

