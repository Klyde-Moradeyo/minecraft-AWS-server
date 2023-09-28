import discord
from discord.ext import commands
from logger import setup_logger

# Setting up logger
logger = setup_logger()

class MinecraftBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'{bot.user} has connected to Discord!')

        # Print Connected Server
        logger.info("Connected Servers:")
        for guild in bot.guilds:
            logger.info(f"    - {guild.name}")

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
            for section, help_message in BotConfig.HELP_MESSAGES.items():
                if section != "header" and section != "footer" and section != "features":
                    help_message_content += f"{help_message}\n"
            help_message_content += BotConfig.HELP_MESSAGES["footer"]
            await channel.send(help_message_content)

            if not reset_command_scroll.is_running():
                reset_command_scroll.start()

            # Create a second message (message 2) that will be updated later
            bot_message = await channel.send(bot_response.get_cmd_scroll_msg())
            logger.info(f"bot_message: {bot_message} | {bot_message.id}")

            # Store the bot message ID for this guild
            BotConfig.BOT_MESSAGE_ID[guild.id] = bot_message.id
            logger.info(f"MESSAGE_ID: {BotConfig.BOT_MESSAGE_ID}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == bot.user:
            return

        # Only process commands in the Mango-Minecraft channel
        if message.channel.name == BotConfig.CHANNEL_NAME:
            if message.content.startswith("Hello"):
                await message.channel.send("Hello!")
            await message.delete()  # delete the user's message
            await bot.process_commands(message)

    @commands.command()
    async def start(self, context, game_mode: str = 'VANILLA'):
        """
        Starts the Minecraft server.
        """
        # if game_mode.upper() not in ['VANILLA']:
        #     await context.send(f"Invalid game mode: {game_mode}. Please use a valid game mode.")
        #     return
        command = Command(context, "start")
        await command.execute()
        
    @commands.command(name='status')
    async def get_server_status(self, context):
        """
        Checks the status of the Minecraft server.
        """
        command = Command(context, "status")
        await command.execute()
        
    @commands.command()
    async def stop(self, context):
        """
        Stops the Minecraft server.
        """
        command = Command(context, "stop")
        await command.execute()

    @commands.command()
    async def features(self, context):
        """
        Show Minecraft server Features
        """
        command = Command(context, "features")
        await command.execute()

    @commands.command()
    async def mc_world_archive(self, context):
        """
        Compress the Minecraft World Repository - Only Developers can use this command
        """
        command = Command(context, "mc_world_archive")
        await command.execute()

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.add_cog(MinecraftBot(bot))
    bot.run(BotConfig.TOKEN)
