# Discord Dev Portal: http://discordapp.com/developers/applications

import discord
from discord.ext import commands
import os

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

# On Message Event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("Hello"):
        await message.channel.send("Hello!")

    await bot.process_commands(message)  # Add this line to allow command processing

# Start minecraft server
@bot.command()
async def start(context):
    await context.send("starting minecraft server")

@bot.command(name='status')
async def get_server_status(context):
    # get server ver, 
    # get if online
    await context.send("server status")

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