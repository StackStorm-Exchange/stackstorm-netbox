import json

from lib.action import NetboxBaseAction
from st2client.client import Client
from st2client.models import KeyValuePair


class NetboxHTTPAction(NetboxBaseAction):
    """
    Action to call netbox api and return response.
    """

    def run(self, endpoint_uri, http_verb, get_detail_route_eligible, fail_non_2xx, **kwargs):
        """
        StackStorm action entry point.
        """
        if http_verb == "get":
            if kwargs.get("id", False) and get_detail_route_eligible:
                # modify the `endpoint_uri` to use the detail route
                endpoint_uri = "{}{}/".format(endpoint_uri, str(kwargs.pop("id")))
                self.logger.debug(
                    "endpoint_uri transformed to {} because id was passed".format(endpoint_uri)
                )

            if kwargs.get("save_in_key_store") and not kwargs.get("save_in_key_store_key_name"):
                return (False, "save_in_key_store_key_name MUST be used with save_in_key_store!")

            result = self.make_request(endpoint_uri, http_verb, **kwargs)

            if fail_non_2xx:
                # Return error rather than storing it in the keystone.
                if result["status"] not in range(200, 300):
                    return (False, result)

            if kwargs["save_in_key_store"]:
                # save the result in the st2 keystore
                client = Client(base_url="http://localhost")
                key_name = kwargs["save_in_key_store_key_name"]
                client.keys.update(
                    KeyValuePair(
                        name=key_name, value=json.dumps(result), ttl=kwargs["save_in_key_store_ttl"]
                    )
                )

                return (True, "Result stored in st2 key {}".format(key_name))

        else:
            result = self.make_request(endpoint_uri, http_verb, **kwargs)

        # To maintain backward compatibility, this action always returns True (success) event
        # when the netbox http return status is not OK.  action_succeeded is set to True and
        # will only be set to False if the `fail_non_2xx` argument is set to True _and_ netbox
        # http return code is not 2xx.
        action_succeeded = True

        if fail_non_2xx:
            action_succeeded = result.get("status") in range(200, 300)

        return (action_succeeded, result)
