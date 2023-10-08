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

class MinecraftBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = setup_logging() # Setting up logger
        self.channel_manager = ChannelManager(DISCORD_CHANNEL_CATEGORY_NAME, DISCORD_CHANNEL_NAME)
        self.file_helper = FileHelper()

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"'{bot.user}' has connected to Discord!")  

        info_msg = MessageManager()
        command_scroll_msg = MessageManager()

        # Loop through discord servers and 
        for guild in bot.guilds:
            channel = await self.channel_manager.create_channel(guild) # Create channels

            # Remove Previous Contents from the channel
            await channel.purge(limit=None)

            # Print Initilizing message
            init_yml = YamlHelper(yaml_str=INIT_MSG)
            message = info_msg.construct_message_from_dict(init_yml.get_data())
            await info_msg.send_new_msg(channel, message)
            self.logger.info("Sent Initilization Message...")   

            # Load yaml file
            bot_message_yml = YamlHelper(BOT_MSG_PATH)

            # Perform Health Check - WIP
            self.logger.info("Performing Health Checks...")
            time.sleep(2)

            # Send Version Message
            bot_ver, lambda_ver, fargate_ver, infra_ver = HealthCheck.get_version()
            version_variables = {
                "DISCORD_BOT_VER": str(bot_ver),
                "LAMBDA_VER": str(lambda_ver),
                "FARGATE_VER": str(fargate_ver),
                "INFRA_VER": str(infra_ver)
            }
            bot_message_yml.resolve_placeholders(version_variables)
            version_yml_data = bot_message_yml.get_data()["VERSION"]
            message = info_msg.construct_message_from_dict(version_yml_data)
            await info_msg.edit_msg(channel, message)
            self.logger.info("Sent Version Message...")  
            time.sleep(5) 

            # if not reset_command_scroll.is_running():
            #     reset_command_scroll.start()

            # # Create a second message (message 2) that will be updated later
            # bot_message = await channel.send(bot_response.get_cmd_scroll_msg())
            # self.logger.info(f"bot_message: {bot_message} | {bot_message.id}")

            # # Store the bot message ID for this guild
            # BotConfig.BOT_MESSAGE_ID[guild.id] = bot_message.id
            # self.logger.info(f"MESSAGE_ID: {BotConfig.BOT_MESSAGE_ID}")

            # Log Connected Servers to console
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

