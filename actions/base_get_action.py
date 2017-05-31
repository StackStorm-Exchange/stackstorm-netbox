
from lib.action import NetboxBaseAction


class NetboxBaseGetAction(NetboxBaseAction):
    """Base get action"""

    def run(self, endpoint_uri, **kwargs):
        """Base get action
        endpoint_uri is pased from metadata file
        """
        return self.get(endpoint_uri, **kwargs)
