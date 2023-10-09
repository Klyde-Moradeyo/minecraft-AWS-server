import os

##### Maintenance Mode #####
IS_MAINTENANCE = False

##### DISCORD VARS #####
DISCORD_CHANNEL_NAME = "mango-minecraft"
DISCORD_CHANNEL_CATEGORY_NAME = "BOT"

##### BOT INIT MESSAGE #####
INIT_MSG = """
INIT_MSG:
  - "------------------------------------------------------------------------------------------------------------"
  - "                                  🛠️ Initialization in progress... ⚙️                                      "
  - "------------------------------------------------------------------------------------------------------------"
"""

##### DATA PATHS #####
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_MSG_PATH = os.path.join(BASE_DIR, "data", "bot_messages.yml")

##### Roles #####
ADMIN_ROLE_NAME = "Minecraft-Admin"



