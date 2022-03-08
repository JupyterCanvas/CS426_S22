# systemd services

## network namespace configuration

### Allow process running as an unprivileged user to use a private network namespace

- Unprivledged users can not use ip netns exec when starting container. 

- Let systemd create the namespace, subsequent units join namespace and subsequent joins can be unprivledged. 

- systemd does not support named network interfaces. Combine with ip netns namespaces to work around (source https://github.com/systemd/systemd/issues/2741#issuecomment-433979748)

- Use systemd template units and EnvironmentFiles to create unit instances

- Use systemd BindTo+After to link instance service dependencies: 

    `systemctl start testnetns@12310.service` starts: 
    - an instance of the testnetns service, 
    - it also creates a nsbr@12310.service instance, 
    - which creates a netns@12310.service instance. 
    - only call the sub unit service and its dependencies are generated automatically. 

    
    The network bridge is not part of the dependency stack. Run the bridge service file before the netns services. 

    Removing the network namespace also removes the veth pair
    
    `ip netns list`
    
    `ip netns delete ns12310`
---
