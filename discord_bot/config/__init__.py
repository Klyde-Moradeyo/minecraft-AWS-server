import os

##### Maintenance Mode #####
IS_MAINTENANCE = False

##### DISCORD VARS #####
DISCORD_CHANNEL_NAME = "mango-minecraft"
DISCORD_CHANNEL_CATEGORY_NAME = "BOT"

##### BOT INIT MESSAGE #####
INIT_MSG = """
ON_INIT:
  - "------------------------------------------------------------------"
  - "                🛠️ Discord Bot Initializating... ⚙️              "
  - "------------------------------------------------------------------"
UPDATING:
  - "------------------------------------------------------------------"
  - "                 🛠️ Discord Bot Updating... ⚙️              "
  - "------------------------------------------------------------------"
"""

## RESET COMMAND SCROLL CHECK INTERVAL
RESET_COMMAND_SCROLL_CHECK_INTERVAL = 1 # seconds
RESET_COMMAND_SCROLL_TIME = 5 # seconds

##### DATA PATHS #####
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_MSG_PATH = os.path.join(BASE_DIR, "data", "bot_messages.yml")

##### State Management #####
CHANNEL_STATE_FILE = os.path.join(BASE_DIR, "state", "channel_state.json")
MESSAGE_STATE_FILE = os.path.join(BASE_DIR, "state", "message_state.json")
SCHEDULER_STATE_FILE = os.path.join(BASE_DIR, "state", "scheduler_state.json")

##### Roles #####
ADMIN_ROLE_NAME = "Minecraft-Admin"





