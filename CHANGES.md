# Change Log

## 3.4.1

- Updated spec as per v3.7.3

## 3.4.0

- Updated spec as per v3.7.1

## 3.3.0

- Updated spec as per v3.6.9

## 3.2.0

- Update spec as per v3.5.9

## 3.1.0

- Updated spec as per v3.4.7

## 3.0.7

- Add @abhi1693 as code owner.

## 3.0.6

- Add exceptions on action.py

## 3.0.5

- Bug fix: Tags fields need additional translation when modifying 

## 3.0.4

- Bug fix: PATCH requests don't need all the fields to be required 

## 3.0.3

- Updated spec as per v3.1.7

## 3.0.2

- Updated templates to remove date
- Fixed data type to be always lower

## 3.0.1

- Added status code to the response

## 3.0.0

- Updated actions generated to cover all routes available in the NetBox 3.1 API.

## 2.0.0

- Drop Python 2.7 support

## 1.1.1
- Version bump to fix tagging issue, no code changes.

## 1.1.0
- Added the `netbox_webhooks` sensor which listens for inbound webhooks from NetBox and fires triggers into StackStorm.

## 1.0.0

- Added script in `/bin` to auto generate all action meta definitions based on the NetBox OpenAPI (Swagger) spec.
- All actions rewritten (auto generated) based on the new mechanism. Note existing actions have been renamed (see Breaking changes)
- New actions generated to cover all routes available in the NetBox 2.4 API.

### Breaking changes
- All pre-existing actions have been renamed to conform to a new, consistent naming scheme. That scheme is `<http_verb>.<app>.<route>`

## 0.5.0
- Added proper application/json Content-Type header to all requests

## 0.4.2
- Changed the `id` parameter on `ipam_post_available_ips` to `prefix_id` so it does not auto convert to a detail route

## 0.4.1
- Fixed `ipam_post_available_ips` to use correct parameters

## 0.4.0
- Added support for virtualization enpoints
  - GET: clusters, cluster groups, cluster types, virtual machine interfaces, virtual machines
  - POST, PUT, PATCH: virtual machines, virtual machine interfaces
- Added support for converting to the detail route by passing the `id` parameter on all applicable endpoints. This converts the api route to `<endpoint_uri>/<id>/` which will always return a max of one entity, instead of a list of zero or more entities.

## 0.3.2
- Added new action for getting device interface connections.

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
