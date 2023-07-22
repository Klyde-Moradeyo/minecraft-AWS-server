# Discord Dev Portal: http://discordapp.com/developers/applications
# Requires Environment variables
#   - DISCORD_TOKEN
#   - API_URL

import discord
from discord.ext import commands
import os
import requests
import json
import tempfile
import logging
from bot_reply import Bot_Response

logging.basicConfig(level=logging.DEBUG)

# Initilize bot reply
bot_response = Bot_Response()

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

    HELP_MESSAGES = {
        "header": "🥭 **Mango Minecraft Guidebook** 🗺️\n\n" +
                   f"🏡 IP: `{SERVER_IP}:25565`\n" +
                   "⚙️ Version: `1.20.1`\n\n" +
                   "✨ **Features:**\n" +
                   "- **Multiplayer Sleep:** 💤 A single player can sleep and skip the night for everyone.\n" +
                   "- **Coordinates HUD:** 📍 Coordinates and 24-hour clock display above the hotbar using `/trigger ch_toggle`\n" +
                   "- **Armour Status:** 🛡️ Modify and pose armor stands using a special book.\n" +
                   "- **Custom Nether Portal:** 🔥 Create Nether portals of any shape or size, even with crying obsidian.\n" +
                   "- **Item Averages:** 💡 Count items passing through a given spot.\n" +
                   "- **Larger Phantoms:** 🦇 Creates larger phantoms based on how long since you last slept.\n" +
                   "- **Real-Time Clock:** ⏰ Trigger to let you see how long a Minecraft world has been running.\n" +
                   "- **Village Death Message:** 💔 Villager death messages.\n" +
                   "- **XP Management:** 💼 Right-Click an enchantment table with an empty bottle to fill it with some of your XP.\n\n" +
                   "🛠️ **Commands:**",
        "start": "- **start**: 🚀 Use this command to start the Minecraft server! Just type `!start` and watch the magic happen.",
        "status": "- **status**: 🔍 Type `!status` and I'll get the latest updates for you.",
        "stop": "- **stop**: 🛑 Want to pause your Minecraft journey for now? Type `!stop` and the server will safely stop, allowing you to resume later",
        "footer": "------------------------------------------------------------------------------------------------------------"
    }

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

    url += "/minecraft-prod/command"
    
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

######################################################################
#                       MinecraftCommand                             #
######################################################################
# Helper function to handle common logic in bot commands
class MinecraftCommand:
    VALID_COMMANDS = ["start", "stop", "status"]

    def __init__(self, context, command):
        self.context = context
        self.command = command
        self.bot_message = None

    async def execute(self):
        if self.command not in self.VALID_COMMANDS:
            await self.on_error(f"Invalid command: {self.command}. Please use a valid command.")
            return
        try:
            # Fetch the channel and bot message ID specific to the guild
            channel_id = BotConfig.CHANNEL_ID[self.context.guild.id]
            bot_message_id = BotConfig.BOT_MESSAGE_ID[self.context.guild.id]

            channel = await bot.fetch_channel(channel_id)
            self.bot_message = await channel.fetch_message(bot_message_id)

            await self.bot_message.edit(content=f"User {self.context.author.name} used `{self.command}` command...")
            data = { "command": self.command }
            response = send_to_api(data)
            logging.info(f"response: {response}")
            
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

            # Edit Discord Message
            logging.info(f"BOT_REPLY: {BOT_REPLY}")
            await self.bot_message.edit(content=BOT_REPLY)
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
        for command, help_message in BotConfig.HELP_MESSAGES.items():
            if command != "header" and command != "footer":
                help_message_content += f"{help_message}\n"
        help_message_content += BotConfig.HELP_MESSAGES["footer"]
        await channel.send(help_message_content)

        # Create a second message (message 2) that will be updated later
        bot_message = await channel.send("📜 The command scroll is at your service 🔮")
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
async def start(context):
    """
    Starts the Minecraft server.
    """
    command = MinecraftCommand(context, "start")
    await command.execute()

# Check Server Status
@bot.command(name='status')
async def get_server_status(context):
    """
    Checks the status of the Minecraft server.
    """
    command = MinecraftCommand(context, "status")
    await command.execute()

# Stop minecraft server
@bot.command()
async def stop(context):
    """
    Stops the Minecraft server.
    """
    command = MinecraftCommand(context, "stop")
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