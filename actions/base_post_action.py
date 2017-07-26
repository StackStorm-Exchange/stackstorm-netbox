
from lib.action import NetboxBaseAction


class NetboxBasePostAction(NetboxBaseAction):
    """Base get action"""

    def run(self, endpoint_uri, **kwargs):
        """Base get action
        endpoint_uri is pased from metadata file
        """
        return self.post(endpoint_uri, **kwargs)

