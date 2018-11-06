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

There are more than 290 actions in this pack. Each maps to a particular NetBox API endpoint.

The action naming convention is easy to understand as it follows this basic pattern:
```
<http_verb>.<netbox_app>.<netbox_model>
```

Example for the action to make a GET request for Sites:
```
get.dcim.sites
```

Each action has been auto generated based on the NetBox OpenAPI (Swagger) spec file. The actions are periodically updated in accordance with new NetBox releases. Check the [change log](CHANGES.md) for details.

All GET actions have the ability to store the NetBox API response directly into the ST2 Key Store rather than provide it as standard action output. This is useful in cases where that reponse is extremely large and thus passing it between actions is impractical. This is controlled with the `save_in_key_store`, `save_in_key_store_key_name`, and `save_in_key_store_ttl` action parameters. Look at any `get.*` action meta file for more details.
