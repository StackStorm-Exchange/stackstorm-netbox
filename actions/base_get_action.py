
import json

from lib.action import NetboxBaseAction
from st2client.client import Client
from st2client.models import KeyValuePair


class NetboxBaseGetAction(NetboxBaseAction):
    """Base get action"""

    def run(self, endpoint_uri, **kwargs):
        """Base get action
        endpoint_uri is pased from metadata file
        """

        if kwargs.get('save_in_key_store') and not kwargs.get('save_in_key_store_key_name'):
            return (False, 'save_in_key_store_key_name MUST be used with save_in_key_store!')

        result = self.get(endpoint_uri, **kwargs)

        if kwargs['save_in_key_store']:
            # save the result in the st2 keystore
            client = Client(base_url='http://localhost')
            key_name = kwargs['save_in_key_store_key_name']
            client.keys.update(KeyValuePair(name=key_name, value=json.dumps(result)),
                               ttl=kwargs['save_in_key_store_ttl'])

            return (True, "Result stored in st2 key {}".format(key_name))

        return self.get(endpoint_uri, **kwargs)
