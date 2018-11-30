import hashlib
import hmac

from flask import request, Flask

from st2reactor.sensor.base import Sensor


class NetBoxWebhooksSensor(Sensor):
    def __init__(self, sensor_service, config):
        super(NetBoxWebhooksSensor, self).__init__(
            sensor_service=sensor_service,
            config=config
        )

        self._host = config.get('sensor_address', '0.0.0.0')
        self._port = config.get('sensor_port', 6000)
        self._path = '/netbox/webhooks/'
        self._secret = config.get('sensor_secret', "")

        self._log = self._sensor_service.get_logger(__name__)
        self._app = Flask(__name__)

    def setup(self):
        pass

    def run(self):
        @self._app.route(self._path, methods=['POST'])
        def event():

            if self._secret:
                hmac_prep = hmac.new(
                    key=self._secret.encode('utf8'),
                    msg=request.get_data().encode('utf8'),
                    digestmod=hashlib.sha512
                )
                if request.headers.get('X-Hook-Signature') != hmac_prep.hexdigest():
                    self._log.warning("Failed to verify request signature.")
                    return "Nope", 400
                else:
                    self._log.info("Request passed signature verification.")

            payload = request.get_json(force=True)

            event = payload.get('event', None)
            if event == 'created':
                trigger = "netbox.webhook.object_created"
            elif event == 'updated':
                trigger = "netbox.webhook.object_updated"
            elif event == 'deleted':
                trigger = "netbox.webhook.object_deleted"
            else:
                self._log.warning("Unknown event request received, refusing to process.")
                return "Nope", 400

            self._sensor_service.dispatch(trigger=trigger, payload=payload)
            return "Done", 200

        self._log.info('Listening for payload on http://{}:{}{}'.format(
            self._host, self._port, self._path))
        self._app.run(host=self._host, port=self._port, threaded=False)

    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        # This method is called when trigger is created
        pass

    def update_trigger(self, trigger):
        # This method is called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # This method is called when trigger is deleted
        pass
