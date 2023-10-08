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

class MinecraftBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = setup_logging() # Setting up logger
        self.envs = EnvironmentVariables().get_vars()
        self.channel_manager = ChannelManager(DISCORD_CHANNEL_CATEGORY_NAME, DISCORD_CHANNEL_NAME)
        self.file_helper = FileHelper()

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"'{bot.user}' has connected to Discord!")  

        # Init MessageManagers
        info_msg = MessageManager()
        command_scroll_msg = MessageManager()

        # Loop through discord servers and 
        for guild in bot.guilds:
            channel = await self.channel_manager.create_channel(guild) # Create channels

            # Remove Previous Contents from the channel
            await channel.purge(limit=None)

            # Print Initilizing message
            self.logger.info("Sending Initilization Message...")  
            init_yml = YamlHelper(yaml_str=INIT_MSG)
            message = info_msg.construct_message_from_dict(init_yml.get_data())
            await info_msg.send_new_msg(channel, message)
             
            # Load yaml file
            bot_message_yml = YamlHelper(BOT_MSG_PATH)

            # Perform Health Check - WIP
            self.logger.info("Performing Health Checks...")
            health_check = HealthCheck()
            bot_ver, lambda_ver, fargate_ver, infra_ver = health_check.get_version()
            time.sleep(2)

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

            # Send Version Message
            self.logger.info("Sending Version Message...")  
            message = info_msg.construct_message_from_dict(bot_message_yml.get_data()["VERSION"])
            await info_msg.edit_msg(channel, message)
            time.sleep(5) 


            # Update Info Message to show User Guide
            self.logger.info("Sending User Guide Message...")  
            message = info_msg.construct_message_from_dict(bot_message_yml.get_data()["USER_GUIDE"]) 
            await info_msg.edit_msg(channel, message)

        # Init Bot Responses
        bot_response = BotResponse(bot_message_yml.get_data())

        self.logger.info("Sending User Command Scroll Message...")  
        for guild in bot.guilds:
            message = bot_response.get_cmd_scroll_msg()
            await command_scroll_msg.send_new_msg(channel, message)

        # Log connected servers
        guild_names = [guild.name for guild in bot.guilds]
        self.logger.info(f"Connected to Servers: {guild_names}")

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author == bot.user:
    #         return

    #     # Only process commands in the Mango-Minecraft channel
    #     if message.channel.name == BotConfig.CHANNEL_NAME:
    #         if message.content.startswith("Hello"):
    #             await message.channel.send("Hello!")
    #         await message.delete()  # delete the user's message
    #         await bot.process_commands(message)

    # @commands.command()
    # async def start(self, context, game_mode: str = 'VANILLA'):
    #     """
    #     Starts the Minecraft server.
    #     """
    #     # if game_mode.upper() not in ['VANILLA']:
    #     #     await context.send(f"Invalid game mode: {game_mode}. Please use a valid game mode.")
    #     #     return
    #     command = ExecuteCommand(context, "start")
    #     await command.execute()
        
    # @commands.command(name='status')
    # async def get_server_status(self, context):
    #     """
    #     Checks the status of the Minecraft server.
    #     """
    #     command = ExecuteCommand(context, "status")
    #     await command.execute()
        
    # @commands.command()
    # async def stop(self, context):
    #     """
    #     Stops the Minecraft server.
    #     """
    #     command = ExecuteCommand(context, "stop")
    #     await command.execute()

    # @commands.command()
    # async def features(self, context):
    #     """
    #     Show Minecraft server Features
    #     """
    #     command = ExecuteCommand(context, "features")
    #     await command.execute()

    # @commands.command()
    # async def mc_world_archive(self, context):
    #     """
    #     Compress the Minecraft World Repository - Only Developers can use this command
    #     """
    #     command = ExecuteCommand(context, "mc_world_archive")
    #     await command.execute()

if __name__ == '__main__':
    envs = EnvironmentVariables().get_vars()  # Get Environment Variables
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    async def setup_bot():
        await bot.add_cog(MinecraftBot(bot))
        await bot.start(envs["DISCORD_TOKEN"])

    import asyncio
    asyncio.run(setup_bot())

