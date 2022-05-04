# Fail fast
set -o errexit

# Fill this file with your environment creation
./bin/micromamba create -n jupyter-canvas -r /opt/micromamba
eval "$(micromamba shell hook --shell=bash)"
micromamba activate /opt/micromamba/envs/jupyter-canvas

micromamba install -y xeus-cling dotnet-interactive pip -c conda-forge
pip install jupyterlab nbgrader canvasapi nose nbclient==0.5.11 jupyter-server==1.12.0 jupyter-client==6.1.12 traitlets==4.3.3 nbconvert==5.6.1 jupyter-console==6.4.2 jinja2==3.0.3
jupyter nbextension install --sys-prefix --py nbgrader --overwrite
jupyter nbextension enable --sys-prefix --py nbgrader
jupyter serverextension enable --sys-prefix --py nbgrader

