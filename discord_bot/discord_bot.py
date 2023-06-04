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
#                    Helper Functions                                #
######################################################################
file_path = None

def load_bot_message_id():
    try:
        with open("bot_message_id.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return None

def save_bot_message_id(message_id):
    with open("bot_message_id.txt", "w") as f:
        f.write(str(message_id))

bot_message_id = load_bot_message_id()

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

######################################################################
#                  MinecraftCommand Class                            #
######################################################################
# Helper function to handle common logic in bot commands
class MinecraftCommand:
    VALID_COMMANDS = ["start", "stop", "status"]

    def __init__(self, context, command):
        self.context = context
        self.command = command
        self.bot_message = None

    async def execute(self):
        global bot_message_id
        if self.command not in self.VALID_COMMANDS:
            await self.on_error(f"Invalid command: {self.command}. Please use a valid command.")
            return
        try:
            if bot_message_id is not None:
                self.bot_message = await self.context.fetch_message(bot_message_id)
            else:
                self.bot_message = await self.context.send(f"User {self.context.author.name} used `{self.command}` command...")
                bot_message_id = self.bot_message.id
                save_bot_message_id(bot_message_id)

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
#                 CustomHelpCommand Class                            #
######################################################################
class CustomHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f'!{command.name}'

    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        help_content = 'Command:\n'
        for cog, commands in mapping.items():
            if commands:
                filtered = await self.filter_commands(commands, sort=True)
                for command in filtered:
                    help_content += f'- `{command.name}`: {command.help}\n'
        await destination.send(help_content)

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(page)

    def get_destination(self):
        """Gets a `discord.abc.Messageable` to send the help pages to."""
        for guild in self.context.bot.guilds:
            for category in guild.categories:
                if category.name == "BOT":
                    for channel in category.channels:
                        if channel.name == channel_name:
                            return channel
        return self.context.channel  # fallback to the channel the command was invoked from

######################################################################
#                       Discord Bot                                  #
######################################################################
# Discord bot Token
TOKEN = os.environ["DISCORD_TOKEN"]

channel_name = "mango-minecraft"
help_channel_name = "help"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.help_command = CustomHelpCommand()

# Verify that the bot is connected
@bot.event
async def on_ready():
    global bot_message_id
    print(f'{bot.user} has connected to Discord!')
    print("Servers:")
    for guild in bot.guilds:
        print(f"    - {guild.name}")
        category_name = "BOT"  # Specify the category name here:
        category = discord.utils.get(guild.categories, name=category_name)  # Get the category

        if category is None:  # If the category doesn't exist, create it 
            category = await guild.create_category(category_name)

        all_channels = await guild.fetch_channels()  # Fetch all channels from the guild

        category_channels = [channel for channel in all_channels if channel.category == category]  # Filter for the category

        channel = discord.utils.get(category_channels, name=channel_name)  # Check if the channel already exists before creating it
        if channel is None:
            channel = await category.create_text_channel(channel_name)

        await channel.purge(limit=None)  # Clear all messages in the designated channel

        help_channel = discord.utils.get(category_channels, name=help_channel_name)  # Create help channel
        if help_channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                bot.user: discord.PermissionOverwrite(send_messages=True)
            }
            help_channel = await category.create_text_channel(help_channel_name, overwrites=overwrites)

        await help_channel.purge(limit=None)  # Clear all messages in the help channel

        # Get help command context
        help_context = commands.Context(bot=bot, prefix='!', guild=guild, channel=help_channel)
        help_context.command = bot.help_command
        bot.help_command.context = help_context  # Set the context for the help command

        # Send help command to the help channel
        await bot.help_command.send_bot_help(mapping=bot.help_command.get_bot_mapping())

        if bot_message_id is not None:
            bot_message = await channel.fetch_message(bot_message_id)

# On Message Event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only process commands in the Mango-Minecraft channel
    if message.channel.name == channel_name:
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

# @bot.command()
# async def help(context):
#     command = MinecraftCommand(context, "stop")
#     await command.execute()
    

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

