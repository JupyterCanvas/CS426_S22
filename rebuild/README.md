# Rebuild notes:
- Monday 3/07 - accidentally deleted /etc/ directory of project VM
    - created new VM, followed server config notes and pulled in branches from github (some systemd config lost that hadn't been pushed to remote)
- Tuesday 3/08 - realized NGINX server config notes were not with main server config notes
    - attempted to configure NGINX before progress demo, failed, old VM ip hardcoded throughout
    - web server not functional for progress demo
- Created S-rebuild branch to start over with new VM rebuild. 
    - created new repo directory structure to ensure server config notes centralized
    - created scripts for copying files to git directory in system directories such as /etc/systemd/system and /etc/nginx to prevent error that caused project clobbering
    - integrated container and main-S branches from remote repository
    - components from previous build container and main-S branches not included in S-rebuild: 
        - main-S branch: `canvas/05-create_exchange.py`: Creates exchange directory for Jupyter extension nbgrader. Will be added to back to canvas config after new JupyterHub server config. The use of JupyterHub on main server instead of JupyterLab in each container changes this setup. 
        - container branch: JupyterLab install in container (see notes below) may be added back depending on JupyterHub server configuration. As noted in original configuration, can't access systemd services from container, JupyterHub configuration for server should allow JupyterLab instances to be provisioned as services from server instead of from containers. 
            
            ---
            *(start JupyterLab container install notes)*

            ### Install JupyterLab
            shell back in:
            ```bash
            singularity shell --writable debian
            ```
            ```bash
            # in container:
            > apt install -y python3-pip
            > pip install jupyterlab
            # still in container, on mobaxterm
            > jupyter lab # running as rot not recommended
            > jupyter lab --allow-root
            # runs, seems like it doesn't work in browser...
            # but just takes a long time to load in browser from mobaxterm ssh (2.5m)
            ```
            TEST WITH VNC:
            - in container:
            ```bash
            export PATH=/opt/TurboVNC/bin:$PATH
            vncserver
            ```
            - in powershell window: tunnel VNC through SSH
            ```bash
            ssh -L 5901:localhost:5901 root@192.168.161.139
            ```
            - in mobaxterm window:
            ```bash
            hostname = localhost, port = 5901
            password is for vncserver, not server root account
            # open desktop terminal
            jupyter lab --allow-root
            ```
            > desktop GUI loads quickly AND can open JupyterLab quickly!
            - in container:
            ```bash
            vncserver -kill :1
            ```
            ***ISSUES:***
            ASK @ZACH
            > can't run systemctl status jupyter in container. fails with:\
            > `Running in chroot, ignoring request.`
            ---
            - > .DEF CHANGES: install pip, jupyterlab, test jupyter with vnc
            ```bash
            # (in %post, apt installs):
                    python3-pip

                # install JupyterLab
                pip install jupyterlab
            ```
