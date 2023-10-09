# Discord Dev Portal: http://discordapp.com/developers/applications
import discord
import time
import yaml
import asyncio
from discord.ext import commands
from config import *
from utils.logger import setup_logging
from utils.channel_manager import ChannelManager
from utils.message_manager import MessageManager
from utils.file_helper import FileHelper, YamlHelper
from utils.health_checks import HealthCheck
from utils.env_manager import EnvironmentVariables
from utils.bot_response import BotResponse
from utils.commands import ProcessAPICommand
from utils.permision_manager import PermissionManager

class MinecraftBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = setup_logging() # Setting up logger
        self.envs = EnvironmentVariables().get_vars()
        self.channel_manager = ChannelManager(DISCORD_CHANNEL_CATEGORY_NAME, DISCORD_CHANNEL_NAME)
        self.file_helper = FileHelper()
        self.permission_manager = PermissionManager()

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"'{bot.user}' has connected to Discord!")  

        # Init MessageManagers
        self.info_msg = MessageManager()
        self.command_scroll_msg = MessageManager()

        # Loop through discord servers and 
        for guild in bot.guilds:
            channel = await self.channel_manager.create_channel(guild) # Create channels

            # Remove Previous Contents from the channel
            await channel.purge(limit=None)

            # Print Initilizing message
            self.logger.info("Sending Initilization Message...")  
            init_yml = YamlHelper(yaml_str=INIT_MSG)
            message = self.info_msg.construct_message_from_dict(init_yml.get_data())
            await self.info_msg.send_new_msg(channel, message)
             
        # Load yaml file
        bot_message_yml = YamlHelper(BOT_MSG_PATH)

        # Perform Health Check - WIP
        self.logger.info("Performing Health Checks...")
        health_check = HealthCheck()
        bot_ver, lambda_ver, fargate_ver, infra_ver = health_check.get_version()

        # Update bot_messages.yml data
        variables = {
            "SERVER_IP": str(self.envs["SERVER_IP"]),
            "SERVER_PORT": str(self.envs["SERVER_PORT"]),
            "SERVER_VERSION": "N/A until it checks the server",
            "INFRASTRUCTURE_STATUS_MSG": health_check.get_health(),
            "DISCORD_BOT_VER": str(bot_ver),
            "LAMBDA_VER": str(lambda_ver),
            "FARGATE_VER": str(fargate_ver),
            "INFRA_VER": str(infra_ver)
        }
        bot_message_yml.resolve_placeholders(variables)

        # Init Bot Responses
        self.bot_response = BotResponse(bot_message_yml.get_data())

        for guild in bot.guilds:
            channel = self.channel_manager.get_channel(guild)

            # Set Owner and Admins
            self.permission_manager.set_admin(guild)
            self.permission_manager.set_owner(guild)

            # Send Version Message
            self.logger.info("Sending Version Message...")  
            message = self.info_msg.construct_message_from_dict(bot_message_yml.get_data()["VERSION"])
            await self.info_msg.edit_msg(channel, message)

            # Update Info Message to show User Guide
            self.logger.info("Sending User Guide Message...")  
            message = self.info_msg.construct_message_from_dict(bot_message_yml.get_data()["USER_GUIDE"]) 
            await self.info_msg.edit_msg(channel, message)

            self.logger.info("Sending User Command Scroll Message...")  
            message = self.bot_response.get_cmd_scroll_msg()
            await self.command_scroll_msg.send_new_msg(channel, message)

        # Log connected servers
        guild_names = [guild.name for guild in bot.guilds]
        self.logger.info(f"Connected to Servers: {guild_names}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == bot.user:
            return

        # Only process commands in the specified channel
        if message.channel.name == DISCORD_CHANNEL_NAME:
            await message.delete()  # delete the user's message
            if message.content.upper().startswith("PING"):
                await self.command_scroll_msg.edit_msg(message.channel, "PONG")

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if isinstance(error, commands.CommandNotFound):
            message = f"Invalid command: `{context.message.content}`. Please use a valid command."
            await self.command_scroll_msg.edit_msg(context.channel, message)

    @commands.command()
    async def start(self, context):
        """
        Starts the Minecraft server.
        """
        command = ProcessAPICommand(context, "start", self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute()
        
    @commands.command(name='status')
    async def get_server_status(self, context):
        """
        Checks the status of the Minecraft server.
        """
        command = ProcessAPICommand(context, "status", self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute()
        
    @commands.command()
    async def stop(self, context):
        """
        Stops the Minecraft server.
        """
        command = ProcessAPICommand(context, "stop", self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute()

    @commands.command()
    async def mc_world_archive(self, context):
        """
        Compress the Minecraft World Repository - Only Admins can use this command
        """
        command = ProcessAPICommand(context, "mc_world_archive", self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute() 

    # @commands.command()
    # async def features(self, context):
    #     """
    #     Show Minecraft server Features
    #     """
    #     command = ExecuteCommand(context, "features")
    #     await command.execute()

if __name__ == '__main__':
    envs = EnvironmentVariables(True).get_vars()  # Get Environment Variables
    intents = discord.Intents.default()
    intents.members = True  # Enable the members intent
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    async def setup_bot():
        await bot.add_cog(MinecraftBot(bot))
        await bot.start(envs["DISCORD_TOKEN"])

    asyncio.run(setup_bot())

