import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MQTT Configuration
MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))
MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', 60))

# Topics
# Backend communication
TOPIC_BACKEND_TO_BROKER = "backend/broker/commands"
TOPIC_BROKER_TO_BACKEND = "broker/backend/status"

# ROS2 communication
TOPIC_BROKER_TO_ROBOTS = "broker/robots/commands"
TOPIC_ROBOTS_TO_BROKER = "robots/broker/status"

# ROS2 Configuration
ROS2_NODE_NAME = "mqtt_bridge"
ROS2_NAMESPACE = os.getenv('ROS2_NAMESPACE', '') 
