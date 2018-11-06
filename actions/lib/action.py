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

    def make_request(self, endpoint_uri, http_action, **kwargs):
        """Logic to make all types of requests
        """

        if self.config['use_https']:
            url = 'https://'
        else:
            url = 'http://'

        url = url + self.config['hostname'] + "/api" + endpoint_uri

        headers = {
            'Authorization': 'Token ' + self.config['api_token'],
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        # transform `in__id` if present
        if kwargs.get('id__in'):
            kwargs['id__in'] = ','.join(kwargs['id__in'])
            self.logger.debug('id__in transformed to {}'.format(kwargs['id__in']))

        # transform `tags` if present
        if kwargs.get('tags'):
            kwargs['tags'] = ','.join(kwargs['tags'])
            self.logger.debug('tags transformed to {}'.format(kwargs['tags']))

        # strip values which have a None value if we are making a write request
        if http_action != "get":
            kwargs = {key: value for key, value in kwargs.items() if value is not None}

        if http_action == "get":
            self.logger.debug("Calling base get with kwargs: {}".format(kwargs))
            r = requests.get(url, verify=self.config['ssl_verify'], headers=headers, params=kwargs)

        elif http_action == "post":
            self.logger.debug("Calling base post with kwargs: {}".format(kwargs))
            r = requests.post(url, verify=self.config['ssl_verify'], headers=headers, json=kwargs)

        elif http_action == "put":
            self.logger.debug("Calling base put with kwargs: {}".format(kwargs))
            r = requests.put(url, verify=self.config['ssl_verify'], headers=headers, json=kwargs)

        elif http_action == "patch":
            self.logger.debug("Calling base patch with kwargs: {}".format(kwargs))
            r = requests.patch(url, verify=self.config['ssl_verify'], headers=headers, json=kwargs)

        elif http_action == "delete":
            self.logger.debug("Calling base delete with kwargs: {}".format(kwargs))
            r = requests.delete(url, verify=self.config['ssl_verify'], headers=headers)

        return {'raw': r.json()}
