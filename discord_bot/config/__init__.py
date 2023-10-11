import os

##### Maintenance Mode #####
IS_MAINTENANCE = False

##### DISCORD VARS #####
DISCORD_CHANNEL_NAME = "mango-minecraft"
DISCORD_CHANNEL_CATEGORY_NAME = "BOT"

##### BOT INIT MESSAGE #####
INIT_MSG = """
ON_INIT:
  - "-------------------------------------------------------"
  - "         🛠️ Discord Bot Initializating... ⚙️          "
  - "-------------------------------------------------------"
UPDATING:
  - "-------------------------------------------------------"
  - "            ✨ Discord Bot Updating... ✨             "
  - "-------------------------------------------------------"
CMD_SCROLL_DISABLED:
  - "🔮 Command Scroll Disabled 📜"
"""

## RESET COMMAND SCROLL CHECK INTERVAL
RESET_COMMAND_SCROLL_CHECK_INTERVAL = 1 # seconds
RESET_COMMAND_SCROLL_TIME = 5 # seconds


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

##### DATA PATHS #####
BOT_MSG_PATH = os.path.join(BASE_DIR, "data", "bot_messages.yml")

##### STATE MANAGEMENT PATHS #####
CHANNEL_STATE_FILE = os.path.join(BASE_DIR, "state", "channel_state.json")
SCHEDULER_STATE_FILE = os.path.join(BASE_DIR, "state", "scheduler_state.json")

INFO_MSG_MANAGER_STATE_FILE = os.path.join(BASE_DIR, "state", "info_message_state.json")
CMD_SCROLL_MSG_MANAGER_STATE_FILE = os.path.join(BASE_DIR, "state", "cmd_scroll_message_state.json")

##### ROLES #####
ADMIN_ROLE_NAME = "Minecraft-Admin"