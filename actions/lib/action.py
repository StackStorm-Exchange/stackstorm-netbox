from st2common.runners.base_action import Action

import requests


__all__ = [
    'NetboxBaseAction'
]


class NetboxBaseAction(Action):
    """Base Action for all Netbox API based actions
    """

    def __init__(self, config):
        super(NetboxBaseAction, self).__init__(config)

    def _make_request(self, endpoint_uri, http_action, **kwargs):
        """Logic to make all types of requests
        """

        if self.config['use_https']:
            url = 'https://'
        else:
            url = 'http://'

        url = url + self.config['hostname'] + endpoint_uri

        headers = {
            'Authorization': 'Token ' + self.config['api_token'],
            'Accept': 'application/json'
        }

        # transform `in__id` if present
        if kwargs.get('id__in'):
            kwargs['id__in'] = ','.join(kwargs['id__in'])
            self.logger.debug('id__in transformed to {}'.format(kwargs['id__in']))

        if http_action == "GET":
            self.logger.debug("Calling base get with kwargs: {}".format(kwargs))
            r = requests.get(url, verify=self.config['ssl_verify'], headers=headers, params=kwargs)

        elif http_action == "POST":
            self.logger.debug("Calling base post with kwargs: {}".format(kwargs))
            r = requests.post(url, verify=self.config['ssl_verify'], headers=headers, data=kwargs)

        elif http_action == "PUT":
            self.logger.debug("Calling base put with kwargs: {}".format(kwargs))
            r = requests.put(url, verify=self.config['ssl_verify'], headers=headers, data=kwargs)

        elif http_action == "PATCH":
            self.logger.debug("Calling base patch with kwargs: {}".format(kwargs))
            r = requests.patch(url, verify=self.config['ssl_verify'], headers=headers, data=kwargs)

        return {'raw': r.json()}

    def get(self, endpoint_uri, **kwargs):
        """Make a get request to the API URI passed in
        """

        return self._make_request(endpoint_uri, "GET", **kwargs)

    def post(self, endpoint_uri, **kwargs):
        """Make a post request to the API URI passed in
        """

        return self._make_request(endpoint_uri, "POST", **kwargs)

    def put(self, endpoint_uri, **kwargs):
        """Make a put request to the API URI passed in
        """

        return self._make_request(endpoint_uri, "PUT", **kwargs)

    def patch(self, endpoint_uri, **kwargs):
        """Make a patch request to the API URI passed in
        """

        return self._make_request(endpoint_uri, "PATCH", **kwargs)
