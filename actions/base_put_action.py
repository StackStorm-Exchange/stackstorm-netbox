
from lib.action import NetboxBaseAction


class NetboxBasePutAction(NetboxBaseAction):
    """Base put action"""

    def run(self, endpoint_uri, **kwargs):
        """Base put action
        endpoint_uri is pased from metadata file
        """
        return self.put(endpoint_uri, **kwargs)
