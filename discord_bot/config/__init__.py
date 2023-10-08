import os

##### Maintenance Mode #####
ENABLE_MAINTENANCE = False

##### Minecraft Server Config DEFAULTS #####
DEFAULT_VERSION = "1.20.1"
DEFAULT_DIFFICULTY = "hard"
DEFAULT_MODE = "survival"
DEFAULT_EULA = "TRUE"
DEFAULT_MAX_PLAYERS = "20"
DEFAULT_MOTD = "Mango Minecraft Server"
DEFAULT_TYPE = "VANILLA"
DEFAULT_ENABLE_WHITELIST = "FALSE"
DEFAULT_ENFORCE_WHITELIST = "FALSE"
DEFAULT_ANNOUNCE_PLAYER_ACHIEVEMENTS = "true"
DEFAULT_ENABLE_COMMAND_BLOCK = "false"
DEFAULT_TZ = "Europe/London"
DEFAULT_LOG_TIMESTAMP = "true"
DEFAULT_ICON = "xxICONxx"

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



