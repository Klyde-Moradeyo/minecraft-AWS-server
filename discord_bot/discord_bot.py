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
        print(f"{temp_path} doesn't exist")

    return content

def send_to_api(data):
    # API Gateway URL
    url = os.getenv('API_URL')
    if url is None:
        print("API_URL is not set in the environment variables")
        return None

    url += "/minecraft-prod/command"
    
    headers = {'Content-Type': 'application/json'}
    
    print(f"Sending Data to API: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return None

    print(f"Data: {data} \nResponse: \n{response.json()}")  # To print the response from server
    
    return response

# Helper function to handle common logic in bot commands
class MinecraftCommand:
    VALID_COMMANDS = ["start", "stop", "status"]

    def __init__(self, context, command):
        self.context = context
        self.command = command
        self.bot_message = None

    async def execute(self):
        global bot_message
        if self.command not in self.VALID_COMMANDS:
            # await self.context.message.delete()
            await self.on_error(f"Invalid command: {self.command}. Please use a valid command.")
            return
        try:
            # Check if bot_message doesn't exist or was deleted
            if bot_message is None or not bot_message:
                bot_message = await self.context.send(f"User {self.context.author.name} used `{self.command}` command...")
            await self.context.message.delete()
            await bot_message.edit(content=f"User {self.context.author.name} used `{self.command}` command...")
            data = { "command": self.command }
            response = send_to_api(data)
            print(f"response: {response}")
            BOT_REPLY = response.json().get("BOT_REPLY", f"@{self.context.author}, we're sorry but we encountered a problem while processing your request. Please try again in a moment.\nIf the problem persists, don't hesitate to reach out to @The Black Mango for assistance.")
            if response is not None:
                await bot_message.edit(content=BOT_REPLY)
            else:
                await bot_message.edit(content=f"Error: Couldn't {self.command} server.")
        except Exception as e:
            print(str(e))
            await self.on_error(str(e))

    async def on_error(self, error_message):
        if bot_message:
            await bot_message.edit(content=f"Error: \n{error_message}")
        else:
            await self.context.send(f"Error: \n{error_message}")

######################################################################
#                       Discord Bot                                  #
######################################################################
# Discord bot Token
TOKEN = os.environ["DISCORD_TOKEN"]

channel_name = "mango-minecraft"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot_message = None  # Global variable to store the bot message

# Verify that the bot is connected
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Servers:")
    for guild in bot.guilds:
        print(f"    - {guild.name}")

        category_name = "BOT" # Specify the category name here:
        category = discord.utils.get(guild.categories, name=category_name) # Get the category

        # If the category doesn't exist, create it 
        if category is None:
            category = await guild.create_category(category_name)

        # Fetch all channels from the guild
        all_channels = await guild.fetch_channels()

        # Filter for the category
        category_channels = [channel for channel in all_channels if channel.category == category]

        # Check if the channel already exists before creating it
        channel = discord.utils.get(category_channels, name=channel_name)
        if channel is None:
            await category.create_text_channel(channel_name)

# On Message Event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only process commands in the Mango-Minecraft channel
    if message.channel.name == channel_name:
        if message.content.startswith("Hello"):
            await message.channel.send("Hello!")

        await bot.process_commands(message)

# Start minecraft server
@bot.command()
async def start(context):
    command = MinecraftCommand(context, "start")
    await command.execute()

# Check Server Status
@bot.command(name='status')
async def get_server_status(context):
    command = MinecraftCommand(context, "status")
    await command.execute()

# Stop minecraft server
@bot.command()
async def stop(context):
    command = MinecraftCommand(context, "stop")
    await command.execute()
    

# Start the discord bot
bot.run(TOKEN)

# Useful Commands
# List players
# Get average server startime / run time
# whitelist player
# kick / ban / unban a player
# backup server
# send message to all players
# get server discord usage
# display serve rlogs

