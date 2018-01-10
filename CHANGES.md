# Change Log
## 0.4.0
- Added support for virtualization enpoints
  - GET: cluters, cluster groups, cluster types, virtual machine interfaces, virtual machines
  - POST, PUT, PATCH: virtual machines
- Added support for converting to the detail route by passing the `id` parameter on all applicable endpoints. This converts the api route to `<endpoint_uri>/<id>/` which will always return a max of one entity, instead of a list of zero or more entities.
## 0.3.0
- Added ability to save results into st2 key/value store. Useful when the result from Netbox is very large and will be piped to another action.
## 0.2.1
- Added `role` to dcim_get_devices
## 0.2.0
- Added action to get available IPs from a prefix
- Refactored action.py to allow for POST requests as well as GET
- Added POST version of get_available_ips

## 0.1.1
- Added `limit` and `offset` parameters to all actions

## 0.1.0
- First release

