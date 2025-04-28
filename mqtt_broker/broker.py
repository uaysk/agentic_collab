import paho.mqtt.client as mqtt
import logging
from typing import Callable, Dict

from .config import (
  MQTT_BROKER_HOST,
  MQTT_BROKER_PORT,
  MQTT_KEEPALIVE,
  TOPIC_BACKEND_TO_BROKER,
  TOPIC_BROKER_TO_BACKEND,
  TOPIC_BROKER_TO_ROBOTS,
  TOPIC_ROBOTS_TO_BROKER,
)
from .message_converter import MessageConverter


class MQTTBroker:
  def __init__(self):
    # Initialize MQTT client
    self.mqtt_client = mqtt.Client()
    self.mqtt_client.on_connect = self._on_mqtt_connect
    self.mqtt_client.on_message = self._on_mqtt_message

    # Initialize message converter
    self.converter = MessageConverter()

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)

    # Message handlers
    self._message_handlers: Dict[str, Callable] = {
      TOPIC_BACKEND_TO_BROKER: self._handle_backend_message,
      TOPIC_ROBOTS_TO_BROKER: self._handle_robots_message,
    }

  def start(self):
    """Start the MQTT broker service."""
    try:
      # Connect to MQTT broker
      self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
      self.mqtt_client.loop_start()

      # Subscribe to all relevant topics
      for topic in self._message_handlers.keys():
        self.mqtt_client.subscribe(topic)
        self.logger.info(f"Subscribed to topic: {topic}")

      self.logger.info("MQTT Broker service started successfully")

    except Exception as e:
      self.logger.error(f"Failed to start MQTT Broker: {e}")
      raise

  def stop(self):
    """Stop the MQTT broker service."""
    self.mqtt_client.loop_stop()
    self.mqtt_client.disconnect()
    self.logger.info("MQTT Broker service stopped")

  def _on_mqtt_connect(self, client, userdata, flags, rc):
    """Callback for MQTT connection."""
    if rc == 0:
      self.logger.info("Connected to MQTT broker")
    else:
      self.logger.error(f"Failed to connect to MQTT broker with code: {rc}")

  def _on_mqtt_message(self, client, userdata, msg):
    """Callback for MQTT messages."""
    try:
      topic = msg.topic
      payload = msg.payload.decode("utf-8")

      if topic in self._message_handlers:
        self._message_handlers[topic](payload)
      else:
        self.logger.warning(f"Received message on unknown topic: {topic}")

    except Exception as e:
      self.logger.error(f"Error processing MQTT message: {e}")

  def _handle_backend_message(self, message: str):
    """Handle messages from backend."""
    try:
      if self.converter.validate_message(message):
        # Convert message to robot format
        robot_message = self.converter.backend_to_robots(message)
        # Publish to robot topic
        self.mqtt_client.publish(TOPIC_BROKER_TO_ROBOTS, robot_message)
        self.logger.info("Converted and forwarded backend message to robot")
    except Exception as e:
      self.logger.error(f"Error handling backend message: {e}")

  def _handle_robots_message(self, message: str):
    """Handle messages from robot."""
    try:
      if self.converter.validate_message(message):
        # Convert message to backend format
        backend_message = self.converter.robots_to_backend(message)
        # Publish to backend topic
        self.mqtt_client.publish(TOPIC_BROKER_TO_BACKEND, backend_message)
        self.logger.info("Converted and forwarded robot message to backend")
    except Exception as e:
      self.logger.error(f"Error handling robot message: {e}")


def main():
  broker = MQTTBroker()

  try:
    broker.start()
    # Keep the service running
    while True:
      pass
  except KeyboardInterrupt:
    pass
  finally:
    broker.stop()


if __name__ == "__main__":
  main()
