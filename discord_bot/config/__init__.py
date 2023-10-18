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

 ##### RESET COMMAND SCROLL CHECK INTERVAL  #####
RESET_COMMAND_SCROLL_CHECK_INTERVAL = 60 # seconds
RESET_COMMAND_SCROLL_TIME = 300 # seconds

##### POLL MINECRFAFT SERVER ONLINE CHECK INTERVAL  #####
POLL_MC_SERVER_ONLINE_CHECK_INTERVAL = 5 # seconds

##### RESET MC ONLINE PRIVATE DM INTERVAL  #####
RESET_PRIVATE_ONLINE_MSG_CHECK_INTERVAL = 300 # seconds
RESET_PRIVATE_ONLINE_MSG_TIME = 1800 # seconds

##### PERIODIC HEALTH CHECK INTERVAL  #####
PERIODIC_HEALTH_CHECK_INTERVAL = 360 # seconds

##### ROLES #####
ADMIN_ROLE_NAME = "Minecraft-Admin"

##### PATHS #####
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
##### DATA PATHS #####
BOT_MSG_PATH = os.path.join(BASE_DIR, "data", "bot_messages.yml")
##### STATE MANAGEMENT PATHS #####
CHANNEL_STATE_FILE = os.path.join(BASE_DIR, "state", "channel_state.json")
SCHEDULER_STATE_FILE = os.path.join(BASE_DIR, "state", "scheduler_state.json")
INFO_MSG_MANAGER_STATE_FILE = os.path.join(BASE_DIR, "state", "info_message_state.json")
CMD_SCROLL_MSG_MANAGER_STATE_FILE = os.path.join(BASE_DIR, "state", "cmd_scroll_message_state.json")