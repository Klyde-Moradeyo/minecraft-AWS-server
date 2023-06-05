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

logging.basicConfig(level=logging.DEBUG)

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

    HELP_MESSAGES = {
        "header": "🥭 **Mango Minecraft Guidebook** 🗺️\n\n" +
                   "🏡 IP: `52.56.39.89:25565`\n" +
                   "⚙️ Version: `1.19.2`\n\n" +
                   "✨ **Features:**\n" +
                   "**Multiplayer Sleep:** 💤 A single player can sleep and skip the night for everyone.\n" +
                   "**Coordinates HUD:** 📍 Coordinates and 24-hour clock display above the hotbar using `/trigger ch_toggle`\n" +
                   "**Armour Status:** 🛡️ Modify and pose armor stands using a special book.\n" +
                   "**Custom Nether Portal:** 🔥 Create Nether portals of any shape or size, even with crying obsidian.\n" +
                   "**Item Averages:** 💡 Count items passing through a given spot.\n" +
                   " **Larger Phantoms:** 🦇 Creates larger phantoms based on how long since you last slept.\n" +
                   "**Real-Time Clock:** ⏰ Trigger to let you see how long a Minecraft world has been running.\n" +
                   "**Village Death Message:** 💔 Villager death messages.\n" +
                   "**XP Management:** 💼 Right-Click an enchantment table with an empty bottle to fill it with some of your XP.\n\n" +
                   "🛠️ **Commands:**",
        "start": "**!start**: 🚀 Start the Minecraft server. Command: `!start`",
        "status": "**!status**: 🔍 Get the latest updates. Command: `!status`",
        "stop": "**!stop**: 🛑 Stop the Minecraft server. Command: `!stop`",
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
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        return None

    logging.info(f"Data: {data} \nResponse: \n{response.json()}")  # To print the response from server
    
    return response

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
            BOT_REPLY = response.json().get("BOT_REPLY", f"@{self.context.author}, we're sorry but we encountered a problem while processing your request. Please try again in a moment.\nIf the problem persists, don't hesitate to reach out to @The Black Mango for assistance.")
            if response is not None:
                await self.bot_message.edit(content=BOT_REPLY)
            else:
                await self.bot_message.edit(content=f"Error: Couldn't {self.command} server.")
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
    print(f'{bot.user} has connected to Discord!')
    print("Servers:")
    for guild in bot.guilds:
        print(f"    - {guild.name}")

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
        bot_message = await channel.send("📜🔮 The command scroll is at your service")
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