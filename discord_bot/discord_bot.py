# Discord Dev Portal: http://discordapp.com/developers/applications
# Requires Environment variables
#   - DISCORD_TOKEN
#   - API_URL

import discord
from discord.ext import commands, tasks
import os
import requests
import json
import tempfile
import logging
from bot_reply import Bot_Response
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)

# Initilize bot reply
bot_response = Bot_Response()

# Store the latest command issued in each guild
latest_guild_commands = {}

######################################################################
#                       Configuration                                #
######################################################################
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
    ENABLE_MAINTENANCE = True
    MAINTENANCE_BYPASS_USERS = [ os.environ["DEV_DISCORD_ACCOUNT_ID"] ]
    INFRASTRUCTURE_STATUS_MSG = "`MAINTENANCE🔧`"# "`HEALTHY💚`"

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

######################################################################
#                    Helper Functions                                #
######################################################################
file_path = None

# helper function
def write_to_file(content):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write(content)
        temp_path = temp.name
    return temp_path

def read_and_delete_file(temp_path):
    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp:  # Open the file in text mode
            content = temp.read()
    else:
        content = None
        logging.error(f"{temp_path} doesn't exist")
    return content

def send_to_api(data):
    # API Gateway URL
    url = os.getenv('API_URL')
    if url is None:
        print("API_URL is not set in the environment variables")
        return None

    url += "/command"
    
    headers = {'Content-Type': 'application/json'}
    
    logging.info(f"Sending Data to API: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"Data from API: {response}")
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        return None

    logging.info(f"Data: {data} \nResponse: \n{response.json()}")  # To print the response from server
    
    return response

@tasks.loop(seconds=60)  # Check every 60 seconds
async def reset_command_scroll():
    try:
        for guild_id, command in latest_guild_commands.items():
            if datetime.now() - command.datetime > timedelta(minutes=2):  # Reset after 2 minutes
                # Fetch the channel and bot message specific to the guild
                channel = await BotConfig.get_command_scroll_channel(guild_id)
                bot_message = await BotConfig.get_command_scroll_msg(guild_id, channel)

                # Check the current content of bot_message
                if bot_message.content in bot_response.COMMAND_SCROLL:
                    continue

                # Reset the bot message
                await bot_message.edit(content=bot_response.get_cmd_scroll_msg())
                logging.info(f"Resetting command for Guild: {guild_id}, Latest Command: {command.command} | {command.datetime}")
    except Exception as e:
        logging.error(f"Exception in reset_command_scroll: {e}")

######################################################################
#                       Command                                      #
######################################################################
# Helper function to handle common logic in bot commands
class Command:
    VALID_COMMANDS = ["start", "stop", "status", "features", "mc_world_archive"]

    def __init__(self, context, command):
        self.context = context
        self.command = command
        self.bot_message = None
        self.datetime = datetime.now()

    async def execute(self):
        if self.command not in self.VALID_COMMANDS:
            await self.on_error(f"Invalid command: {self.command}. Please use a valid command.")
            return
        try:
            # Fetch the channel and bot message ID specific to the guild
            channel = await BotConfig.get_command_scroll_channel(self.context.guild.id)
            self.bot_message = await BotConfig.get_command_scroll_msg(self.context.guild.id, channel)

            # Inform User their Command is being processed
            BOT_REPLY = f"User {self.context.author.name} used `{self.command}` command..."
            await self.bot_message.edit(content=BOT_REPLY)

            # Maintenance Mode - Only allow Devs to use Discord bot while maintenance mode is ON.
            if BotConfig.ENABLE_MAINTENANCE and str(self.context.author.id) not in BotConfig.MAINTENANCE_BYPASS_USERS:
                BOT_REPLY = bot_response.get_maintenance_msg()
                await self.bot_message.edit(content=BOT_REPLY)
                self.datetime = datetime.now() 
                latest_guild_commands[self.context.guild.id] = self
                return
            
            # 'mc_world_archive' command is for Developers only to use
            if self.command == "mc_world_archive" and str(self.context.author.id) not in BotConfig.MAINTENANCE_BYPASS_USERS:
                BOT_REPLY = bot_response.get_admin_only_reply_msg()
                await self.bot_message.edit(content=BOT_REPLY)
                self.datetime = datetime.now() 
                latest_guild_commands[self.context.guild.id] = self
                return

            if self.command != "features":
                # Send Command to API
                data = { "command": self.command }
                response = send_to_api(data)
    
                # Response will be none if it was unsuccessful
                if response is None:
                    BOT_REPLY = bot_response.api_err_msg()
                else:
                    MC_SERVER_STATUS = response.json().get("STATUS", bot_response.api_err_msg())
                    PREVIOUS_COMMAND = response.json().get("PREVIOUS_COMMAND", None)

                    # If !Status else if start or stop
                    if PREVIOUS_COMMAND is not None:
                        BOT_REPLY = bot_response.msg(PREVIOUS_COMMAND, MC_SERVER_STATUS)
                    else:
                        BOT_REPLY = bot_response.msg(self.command, MC_SERVER_STATUS)
            else:
                BOT_REPLY = BotConfig.HELP_MESSAGES["features"]

            # Log Bot Reply
            logging.info(f"BOT_REPLY: {BOT_REPLY}")

            # Inform User of their commands status
            await self.bot_message.edit(content=BOT_REPLY)

            # Update the datetime after executing the command
            self.datetime = datetime.now() 

            latest_guild_commands[self.context.guild.id] = self
        except Exception as e:
            logging.exception(str(e))
            await self.on_error(str(e))

    async def on_error(self, error_message):
        if self.bot_message:
            await self.bot_message.edit(content=f"Error: \n{error_message}")
        else:
            await self.context.send(f"Error: \n{error_message}")

######################################################################
#                       Discord Bot                                  #
######################################################################
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Verify that the bot is connected
@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    logging.info("Servers:")

    for guild in bot.guilds:
        logging.info(f"    - {guild.name}")

        # Fetch the category, create it if it doesn't exist
        category = discord.utils.get(guild.categories, name=BotConfig.CATEGORY_NAME)
        if category is None:
            category = await guild.create_category(BotConfig.CATEGORY_NAME)

        # Fetch the channel, create it if it doesn't exist
        channel = discord.utils.get(category.text_channels, name=BotConfig.CHANNEL_NAME)
        if channel is None:
            channel = await category.create_text_channel(BotConfig.CHANNEL_NAME)

        # Store the channel ID
        BotConfig.CHANNEL_ID[guild.id] = channel.id

        await channel.purge(limit=None)

        # Create initial help message (message 1)
        help_message_content = BotConfig.HELP_MESSAGES["header"] + "\n"
        for section, help_message in BotConfig.HELP_MESSAGES.items():
            if section != "header" and section != "footer" and section != "features":
                help_message_content += f"{help_message}\n"
        help_message_content += BotConfig.HELP_MESSAGES["footer"]
        await channel.send(help_message_content)

        if not reset_command_scroll.is_running():
            reset_command_scroll.start()

        # Create a second message (message 2) that will be updated later
        bot_message = await channel.send(bot_response.get_cmd_scroll_msg())
        logging.info(f"bot_message: {bot_message} | {bot_message.id}")

        # Store the bot message ID for this guild
        BotConfig.BOT_MESSAGE_ID[guild.id] = bot_message.id
        logging.info(f"MESSAGE_ID: {BotConfig.BOT_MESSAGE_ID}")

# On Message Event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only process commands in the Mango-Minecraft channel
    if message.channel.name == BotConfig.CHANNEL_NAME:
        if message.content.startswith("Hello"):
            await message.channel.send("Hello!")
        await message.delete()  # delete the user's message
        await bot.process_commands(message)

# Start minecraft server
@bot.command()
async def start(context, game_mode: str = 'VANILLA'):
    """
    Starts the Minecraft server.
    """
    # if game_mode.upper() not in ['VANILLA']:
    #     await context.send(f"Invalid game mode: {game_mode}. Please use a valid game mode.")
    #     return
    command = Command(context, "start")
    await command.execute()

# Check Server Status
@bot.command(name='status')
async def get_server_status(context):
    """
    Checks the status of the Minecraft server.
    """
    command = Command(context, "status")
    await command.execute()

# Stop minecraft server
@bot.command()
async def stop(context):
    """
    Stops the Minecraft server.
    """
    command = Command(context, "stop")
    await command.execute()

# Show Minecraft server Features
@bot.command()
async def features(context):
    """
    Show Minecraft server Features
    """
    command = Command(context, "features")
    await command.execute()

# For Running tests
@bot.command()
async def mc_world_archive(context):
    """
    Compress the Minecraft World Repository - Only Developers can use this command
    """
    command = Command(context, "mc_world_archive")
    await command.execute()

# Start the discord bot
bot.run(BotConfig.TOKEN)

# Useful Commands
# List players
# Get average server startime / run time
# whitelist player
# kick / ban / unban a player
# backup server
# send message to all players
# get server discord usage
# display serve rlogs