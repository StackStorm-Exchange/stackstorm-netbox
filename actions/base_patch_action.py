
from lib.action import NetboxBaseAction


class NetboxBasePatchAction(NetboxBaseAction):
    """Base patch action"""

    def run(self, endpoint_uri, **kwargs):
        """Base patch action
        endpoint_uri is pased from metadata file
        """
        return self.patch(endpoint_uri, **kwargs)
