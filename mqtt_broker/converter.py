import json
import numpy as np

from models import BackendToBrokerMessage, RobotsToBrokerMessage, BrokerToRobotsMessage, BrokerToBackendMessage
from coordinate_converter import CoordinateConverter

class MessageConverter:
  def __init__(self):
    sim_origin = (0, 0)
    sim_unit_ft = 0.784
    sim_unit_m = sim_unit_ft / 3.281

    robots_origin_x = 61.1 / sim_unit_ft
    robots_origin_y = 11.36 / sim_unit_ft
    robots_origin = (robots_origin_x, robots_origin_y)
    robots_unit_m = 1

    self.coordinate_converter = CoordinateConverter(
      source_origin=sim_origin,
      target_origin=robots_origin,
      rotation_angle=90,
      scale_factor=robots_unit_m / sim_unit_m,
      reflect_x=False,
      reflect_y=True
    )

  @staticmethod
  def backend_to_robots(mqtt_message: str) -> str:
    """
    Convert backend MQTT message to robot-compatible MQTT format.

    Args:
        mqtt_message: JSON string from backend

    Returns:
        JSON string in robot-compatible format
    """
    try:
      data = json.loads(mqtt_message)
      # Convert backend format to robot format
      # TODO: Implement specific conversion logic based on your message formats
      robot_data = {
        "command": data.get("action", ""),
        "parameters": data.get("params", {}),
        "timestamp": data.get("timestamp", ""),
      }
      return json.dumps(robot_data)
    except json.JSONDecodeError as e:
      raise ValueError(f"Invalid backend message format: {e}")

  @staticmethod
  def robots_to_backend(mqtt_message: str) -> str:
    """
    Convert robot MQTT message to backend-compatible format.

    Args:
        mqtt_message: JSON string from robot

    Returns:
        JSON string in backend-compatible format
    """
    try:
      data = json.loads(mqtt_message)
      # Convert robot format to backend format
      # TODO: Implement specific conversion logic based on your message formats
      backend_data = {
        "status": data.get("state", ""),
        "data": data.get("sensor_data", {}),
        "timestamp": data.get("timestamp", ""),
      }
      return json.dumps(backend_data)
    except json.JSONDecodeError as e:
      raise ValueError(f"Invalid robot message format: {e}")

  @staticmethod
  def validate_message(message: str) -> bool:
    """
    Validate MQTT message format.

    Args:
        message: Message to validate

    Returns:
        True if message is valid JSON, False otherwise
    """
    try:
      json.loads(message)
      return True
    except json.JSONDecodeError:
      return False
