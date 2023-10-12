# Discord Dev Portal: http://discordapp.com/developers/applications
import asyncio
import time
import discord
from discord.ext import commands
from config import *
from utils.logger import setup_logging
from utils.channel_manager import ChannelManager
from utils.message_manager import MessageManager
from utils.file_helper import FileHelper, YamlHelper
from utils.health_checks import HealthCheck
from utils.env_manager import EnvironmentVariables
from utils.bot_response import BotResponse
from utils.process_command import ProcessAPICommand
from utils.permision_manager import PermissionManager
from utils.scheduler import Scheduler
from utils.helpers import DateTimeManager,BotReady

class MinecraftBot(commands.Cog):
    VALID_COMMANDS = {
        "api": { "start", "stop", "status" },
        "features": { "features" },
        "admin_only": { "mc_world_archive" },
        "errors": { 
            "invalid_command": { "invalid_command" }
        }
    }

    def __init__(self, bot):
        self.bot = bot
        self.logger = setup_logging() # Setting up logger
        self.envs = EnvironmentVariables().get_vars()
        self.file_helper = FileHelper()
        self.permission_manager = PermissionManager()
        self.scheduler = Scheduler()
        self.bot_ready = BotReady()
        self.channel_manager = ChannelManager(DISCORD_CHANNEL_CATEGORY_NAME, DISCORD_CHANNEL_NAME)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"'{bot.user}' has connected to Discord!")  

        # Init MessageManagers
        self.info_msg = MessageManager(INFO_MSG_MANAGER_STATE_FILE)
        self.command_scroll_msg = MessageManager(CMD_SCROLL_MSG_MANAGER_STATE_FILE)

        # Loop through discord servers and 
        for guild in bot.guilds:
            channel = await self.channel_manager.create_channel(guild) # Create channels

            # Print Initilizing message
            self.logger.info(f"guild_name: '{guild.name}' - id: '{guild.id}' - Sending Initilization Message...")  
            init_yml = YamlHelper(yaml_str=INIT_MSG)

            if self.info_msg.has_message(channel.id):
                message = self.info_msg.construct_message_from_dict(init_yml.get_data()["UPDATING"])
            else:
                await channel.purge(limit=None)
                message = self.info_msg.construct_message_from_dict(init_yml.get_data()["ON_INIT"])

            # Send info Message
            await self.info_msg.send_new_msg(channel, message)

            # Check If Command Scroll is present
            if self.command_scroll_msg.has_message(channel.id):
                message = self.command_scroll_msg.construct_message_from_dict(init_yml.get_data()["CMD_SCROLL_DISABLED"])
                await self.command_scroll_msg.edit_msg(channel, message)
    
        # Load yaml file
        self.bot_message_yml = YamlHelper(BOT_MSG_PATH)

        # Perform Health Check - WIP
        self.logger.info("Performing Health Checks...")
        health_check = HealthCheck()
        bot_ver, lambda_ver, fargate_ver, infra_ver = health_check.get_version()

        # Update bot_messages.yml data
        variables = {
            "SERVER_IP": str(self.envs["SERVER_IP"]),
            "SERVER_PORT": str(self.envs["SERVER_PORT"]),
            "SERVER_VERSION": "N/A",
            "INFRASTRUCTURE_STATUS_MSG": health_check.get_health(),
            "DISCORD_BOT_VER": str(bot_ver),
            "LAMBDA_VER": str(lambda_ver),
            "FARGATE_VER": str(fargate_ver),
            "INFRA_VER": str(infra_ver)
        }
        self.bot_message_yml.resolve_placeholders(variables)

        # Init Bot Responses
        self.bot_response = BotResponse(self.bot_message_yml.get_data())
        time.sleep(10) # temporary
        for guild in bot.guilds:
            channel = self.channel_manager.get_channel(guild)

            # Set Owner and Admins
            self.permission_manager.set_admin(guild)
            self.permission_manager.set_owner(guild)

            # Send Version Message
            self.logger.info(f"guild_name: '{guild.name}' - id: '{guild.id}' - Sending Version Message...")  
            message = self.info_msg.construct_message_from_dict(self.bot_message_yml.get_data()["VERSION"])
            await self.info_msg.edit_msg(channel, message)

            # Update Info Message to show User Guide
            self.logger.info(f"guild_name: '{guild.name}' - id: '{guild.id}' - Sending User Guide Message...")  
            message = self.info_msg.construct_message_from_dict(self.bot_message_yml.get_data()["USER_GUIDE"]) 
            await self.info_msg.edit_msg(channel, message)

            self.logger.info(f"guild_name: '{guild.name}' - id: '{guild.id}' - Sending User Command Scroll Message...")  
            message = self.bot_response.get_cmd_scroll_msg()
            await self.command_scroll_msg.send_new_msg(channel, message)

        # Log connected servers
        guild_names = [guild.name for guild in bot.guilds]
        self.logger.info(f"Running in Servers: {guild_names}")

        # Start Scheduled Tasks and Checks
        await self.scheduler.add_task("periodic_health_check", self.scheduler.periodic_health_check, 30)

        # Bot is now ready to Process commands
        self.bot_ready.set_status(True)
        self.logger.info(f"------ Discord Bot is Ready('{self.bot_ready.get_status()}') ------")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == bot.user:
            return

        # Only process commands in the specified channel
        if message.channel.name == DISCORD_CHANNEL_NAME:
            await message.delete()  # delete the user's message
            if message.content.upper().startswith("PING") and self.permission_manager.is_admin(message.author.id):
                await self.command_scroll_msg.edit_msg(message.channel, "PONG")

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if isinstance(error, commands.CommandNotFound):
            command = ProcessAPICommand(context, "invalid_command", self.bot_ready, self.VALID_COMMANDS, self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
            await command.execute()

    @commands.command()
    async def start(self, context):
        """
        Starts the Minecraft server.
        """
        command = ProcessAPICommand(context, "start", self.bot_ready, self.VALID_COMMANDS, self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute()
        
    @commands.command(name='status')
    async def get_server_status(self, context):
        """
        Checks the status of the Minecraft server.
        """
        command = ProcessAPICommand(context, "status", self.bot_ready, self.VALID_COMMANDS, self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute()
        
    @commands.command()
    async def stop(self, context):
        """
        Stops the Minecraft server.
        """
        command = ProcessAPICommand(context, "stop", self.bot_ready, self.VALID_COMMANDS, self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute()

    @commands.command()
    async def mc_world_archive(self, context):
        """
        Compress the Minecraft World Repository - Only Admins can use this command
        """
        command = ProcessAPICommand(context, "mc_world_archive", self.bot_ready, self.VALID_COMMANDS, self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute() 

    @commands.command()
    async def features(self, context):
        """
        Show Minecraft server Features
        """
        command = ProcessAPICommand(context, "features", self.bot_ready, self.VALID_COMMANDS, self.envs, self.command_scroll_msg, self.permission_manager, self.bot_response)
        await command.execute() 

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

