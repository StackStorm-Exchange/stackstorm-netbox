# Change Log
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

