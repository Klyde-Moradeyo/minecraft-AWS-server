class BotConfig:
    TOKEN = os.environ["DISCORD_TOKEN"]
    API_URL = os.getenv('API_URL')
    CHANNEL_ID = {}  # Initialize as a dictionary
    CHANNEL_NAME = "mango-minecraft"
    CATEGORY_NAME = "BOT"  # Specify the category name here
    FILE_PATH = None
    BOT_MESSAGE_ID = {}  # Initialize as a dictionary
    SERVER_IP = os.environ["SERVER_IP"]
    SERVER_PORT = "25565"
    SERVER_VERSION = "1.20.1"

    # maintenance config
    # Server status messages: - `HEALTHY💚` - `MAINTENANCE🔧`` - `Issues⚠️ - [REASON] ``
    ENABLE_MAINTENANCE = False
    MAINTENANCE_BYPASS_USERS = [ os.environ["DEV_DISCORD_ACCOUNT_ID"] ]
    INFRASTRUCTURE_STATUS_MSG = "`HEALTHY💚`"

    HELP_MESSAGES = { 
        "header": "🥭 **Mango Minecraft Guidebook** 🗺️\n\n" +
                   f"🏡 IP: `{SERVER_IP}:{SERVER_PORT}`\n" +
                   f"⚙️ Version: `{SERVER_VERSION}`\n" +
                   f"🛡️ System HP: {INFRASTRUCTURE_STATUS_MSG}\n",

        "features": "✨ **Features:**\n" +
                    "- **Multiplayer Sleep:** 💤 A single player can sleep and skip the night for everyone.\n" +
                    "- **Coordinates HUD:** 📍 Coordinates and 24-hour clock display above the hotbar using `/trigger ch_toggle`\n" +
                    "- **Armour Status:** 🛡️ Modify and pose armor stands using a special book.\n" +
                    "- **Custom Nether Portal:** 🔥 Create Nether portals of any shape or size, even with crying obsidian.\n" +
                    "- **Item Averages:** 💡 Count items passing through a given spot.\n" +
                    "- **Larger Phantoms:** 🦇 Creates larger phantoms based on how long since you last slept.\n" +
                    "- **Real-Time Clock:** ⏰ Trigger to let you see how long a Minecraft world has been running.\n" +
                    "- **Village Death Message:** 💔 Villager death messages.\n" +
                    "- **XP Management:** 💼 Right-Click an enchantment table with an empty bottle to fill it with some of your XP.",
                    
        "commands": "🛠️ **Commands:**",
        "start_cmd": "- **start**: 🚀 Use this command to start the Minecraft server! Just type `!start` and watch the magic happen.",
        "status_cmd": "- **status**: 🔍 Type `!status` and I'll get the latest updates for you.",
        "stop_cmd": "- **stop**: 🛑 Want to pause your Minecraft journey for now? Type `!stop` and the server will safely stop, allowing you to resume later",
        "feat_cmd": "- **features**: ✨ Type `!features` to learn about the unique capabilities and tools of the Minecraft server.",

        "footer": "------------------------------------------------------------------------------------------------------------"
    }

    async def get_command_scroll_channel(guild_id):
        channel_id = BotConfig.CHANNEL_ID[guild_id]
        channel = await bot.fetch_channel(channel_id)
        return channel

    async def get_command_scroll_msg(guild_id, channel):
        bot_message_id = BotConfig.BOT_MESSAGE_ID[guild_id]
        bot_message = await channel.fetch_message(bot_message_id)
        return bot_message