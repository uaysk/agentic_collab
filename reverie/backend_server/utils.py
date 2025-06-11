# Copy and paste your OpenAI API Key
openai_api_key = "<Your OpenAI API>"
# Put your name
key_owner = "<Name>"

maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose 
debug = True
use_openai = True
# If you're not using OpenAI, define api_model
api_model = ""
mqtt_host = "localhost"
mqtt_port = "1883"
mqtt_client_id = "reverie_backend"
mqtt_movement_topic = "backend/movement"
mqtt_environment_topic = "gateway/environment"
