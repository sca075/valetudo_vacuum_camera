import logging
import paho.mqtt.client as mqtt

from custom_components.valetudo_vacuum_camera.utils.valetudo_jdata import RawToJson

_LOGGER = logging.getLogger(__name__)


class ValetudoConnector:
    def __init__(self, mqttusr, mqttpass, mqtt_topic, hass):
        self._mqtt_topic = mqtt_topic
        self._broker = "127.0.0.1"
        self._payload = None
        self._data_in = False
        self._mqtt = mqtt.Client("valetudo_connector")
        self._mqtt.on_connect = self.on_connect
        self._mqtt.on_message = self.on_message
        self._mqtt.username_pw_set(username=mqttusr, password=mqttpass)
        self._mqtt.connect_async(host=self._broker)
        self._mqtt.enable_bridge_mode()
        self._mqtt.loop_start()
        self._img_decoder = RawToJson(hass)

    def update_data(self):
        if self._payload:
            _LOGGER.debug("Processing data from MQTT")
            result = self._img_decoder.camera_message_received(self._payload)
            self._data_in = False
            return result
        else:
            self._data_in = False
            return None

    def is_data_available(self):
        return self._data_in

    def on_message(self, client, userdata, msg):
        self._payload = msg.payload
        self._data_in = True
        _LOGGER.debug("Received data from MQTT")


    def on_connect(self, client, userdata, flags, rc):
        _LOGGER.debug("Connected to MQTT broker.")
        self._mqtt.subscribe(self._mqtt_topic)