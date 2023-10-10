import os

##### Maintenance Mode #####
IS_MAINTENANCE = False

##### DISCORD VARS #####
DISCORD_CHANNEL_NAME = "mango-minecraft"
DISCORD_CHANNEL_CATEGORY_NAME = "BOT"

##### BOT INIT MESSAGE #####
INIT_MSG = """
INIT_MSG:
  - "------------------------------------------------------------------"
  - "                🛠️ Discord Bot Initializating... ⚙️              "
  - "------------------------------------------------------------------"
"""

## RESET COMMAND SCROLL CHECK INTERVAL
RESET_COMMAND_SCROLL_CHECK_INTERVAL = 60 # seconds
RESET_COMMAND_SCROLL_TIME = 300 # seconds

##### DATA PATHS #####
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_MSG_PATH = os.path.join(BASE_DIR, "data", "bot_messages.yml")

##### Roles #####
ADMIN_ROLE_NAME = "Minecraft-Admin"


