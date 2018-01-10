# stackstorm-netbox

[NetBox](https://github.com/digitalocean/netbox) is an Open Source IPAM and DCIM tool
maintained by Digital Ocean.

## Configuration

Copy the example configuration in [netbox.yaml.example](./netbox.yaml.example)
to `/opt/stackstorm/configs/netbox.yaml` and edit as required.

It should look like this:

```yaml
---
hostname: "netbox.corp.lan"
api_token: "aaabbbccc111222333"
use_https: true
ssl_verify: true
```

After editing, run `sudo st2ctl reload --register-configs` to ensure your configuration
is loaded.

## Actions

### DCIM
- **dcim\_get\_devices**: Get device(s) via optional parameters
- **dcim\_get\_interfaces**: Get interface(s) via optional parameters
- **dcim\_get\_interface_connections**: Get interface connection(s) via optional parameters
- **dcim\_get\_sites**: Get site(s) via optional parameters

### IPAM
- **ipam\_get\_ip\_addresses**: Get IP Address(es) via optional parameters
- **ipam\_get\_vlan\_groups**: Get VLAN Group(s) via optional parameters
- **ipam\_get\_vlans**: Get VLAN(s) via optional parameters
- **ipam\_get\_vrfs**: Get VRF(s) via optional parameters
- **ipam\_get\_prefixes**: Get Prefix(es) via optional parameters
- **ipam\_get\_available_ips**: Get available IP Address(es) within a prefix
- **ipam\_post\_available_ips**: POST request to create an object assigned to the first available IP address within a given prefix

### Virtualization
- **virtualization\_get\_cluster\_groups**: Get Cluster Group(s) via optional parameters
- **virtualization\_get\_cluster\_types**: Get Cluster Type(s) via optional parameters
- **virtualization\_get\_clusters**: Get Cluster(s) via optional parameters
- **virtualization\_get\_interfaces**: Get Virtual Machine Interface(s) via optional parameters
- **virtualization\_post\_interfaces**: POST request to create a new Virtual Machine Inteface
- **virtualization\_put\_interfaces**: PUT request to replace a Virtual Machine Interface
- **virtualization\_patch\_interfaces**: PATCH request to update a Virtual Machine Interface
- **virtualization\_get\_virtual_machines**: Get Virtual Machine(s) via optional parameters
- **virtualization\_post\_virtual_machines**: POST request to create a new Virtual Machine
- **virtualization\_put\_virtual_machines**: PUT request to replace a Virtual Machine
- **virtualization\_patch\_virtual_machines**: PATCH request to update a Virtual Machine
