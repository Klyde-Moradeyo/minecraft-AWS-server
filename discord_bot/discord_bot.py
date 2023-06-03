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

channel_name = "mango-minecraft"

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
    url = f"{os.environ['API_URL']}/minecraft-prod/command"
    print(url)
    headers = {'Content-Type': 'application/json'}
    print(f"Sending Data to API: {data}")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Data: {data} \nResponse: \n{response.json()}")  # To print the response from server
    return response

######################################################################
#                       Discord Bot                                  #
######################################################################
# Discord bot Token
TOKEN = os.environ["DISCORD_TOKEN"]

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

        category_name = "BOT" # Specify the category name here:
        category = discord.utils.get(guild.categories, name=category_name) # Get the category

        # If the category doesn't exist, create it 
        if category is None:
            category = await guild.create_category(category_name)

        # Check if the channel already exists before creating it
        channel = discord.utils.get(category.text_channels, name=channel_name)
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
    global file_path
    try:
        data = { "command": "start" }
        response = send_to_api(data)
        await context.send(f"starting minecraft server: {response.json()}")
    except Exception as e:
        print(str(e))
        await context.send(f"Error: \n{e}")

# Check Server Status
@bot.command(name='status')
async def get_server_status(context):
    try:
        data = { "command": "status"}
        status = send_to_api(data)
        await context.send(f"server status: {status.json()}")
    except Exception as e:
        print(str(e))
        await context.send(f"Error: \n{e}")

# stop minecraft server
@bot.command()
async def stop(context):
    global file_path
    try:
        data = { "command": "stop" }
        response = send_to_api(data)
        await context.send(f"Stopping Minecraft server: {response.json()}")
    except Exception as e:
        print(str(e))
        await context.send(f"Error: \n{e}")
    

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

