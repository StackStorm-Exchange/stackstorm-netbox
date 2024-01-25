# stackstorm-netbox

[NetBox](https://github.com/netbox-community/netbox) is an Open Source IPAM and
DCIM tool originally created by [DigitalOcean](https://www.digitalocean.com/).

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

## Sensors

The pack contains a single sensor meant to interact with the NetBox Webhook functionality. NetBox has the ability to send webhooks to enternal systems when certain user defined events occur. The `netbox_webhooks` sensor is setup to process those events and fire triggers into StackStorm.

The sensor injects three types of triggers based on the webhook event:
- `netbox.webhook.object_created`
- `netbox.webhook.object_updated`
- `netbox.webhook.object_deleted`

The trigger payload contains the entire contents of the webhook data from NetBox.

The sensor exposes three optional pack config parameters to control its operation. This example can be added to the netbox pack config.
```
sensor_address: 192.168.1.100  # defaults 0.0.0.0, making the sensor reachable on all host addresses
sensor_port: 6000  # defaults to 6000
sensor_secret: "<webhook secret>"  # defaults to empty string, which disables signature verification
```
Based on your desired settings, the URL for the webhook's configuration inside of NetBox will be:
```
http://<ip-address>:<port>/netbox/webhooks/
```

**Note:** the sensor does not support HTTPS but this could be accomplished by fronting the sensor with Nginx/Apache/etc, which would terminate the SSL connection and then proxy the request to the sensor over HTTP.

# How to update the pack

The pack is auto generated from the NetBox OpenAPI (Swagger) spec file. To update the pack, follow these steps:

1. Create a virtual environment and install the required dependencies:
```shell
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Change to `bin` directory and run the `generate.py` script:
```shell
cd bin
python generate.py --url https://demo.netbox.dev
```

3. Update the `CHANGES.md` file with the new version of NetBox that was used to generate the pack.
4. Update the `pack.yaml` file with the new version of NetBox that was used to generate the pack.
5. Commit the changes and create a pull request.
6. Once the pull request is merged, a new version of the pack will be released to the StackStorm Exchange.

## Maintainers

Active pack maintainers with review & write repository access and expertise with Netbox:

  - John Anderson <lampwins@gmail.com> @lampwins
  - Abhimanyu Saharan <asaharan@onemindservices.com> @abhi1693
