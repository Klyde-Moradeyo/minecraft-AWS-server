from .api_helper import send_to_api
from .bot_response import Bot_Response
from .bot_config import BotConfig
from .logger import setup_logging

class ExecuteCommand:
    VALID_COMMANDS = ["start", "stop", "status", "features", "mc_world_archive"]

    def __init__(self, context, command):
        self.logger = setup_logging()
        self.context = context
        self.command = command
        self.bot_message = None
        self.datetime = datetime.now()
        self.bot_response = Bot_Response()

    async def execute(self):
        if self.command not in self.VALID_COMMANDS:
            await self.on_error(f"Invalid command: {self.command}. Please use a valid command.")
            return
        try:
            # Fetch the channel and bot message ID specific to the guild
            channel = await BotConfig.get_command_scroll_channel(self.context.guild.id)
            self.bot_message = await BotConfig.get_command_scroll_msg(self.context.guild.id, channel)

            # Inform User their Command is being processed
            BOT_REPLY = f"User {self.context.author.name} used `{self.command}` command..."
            await self.bot_message.edit(content=BOT_REPLY)


            
            # 'mc_world_archive' command is for Developers only to use
            if self.command == "mc_world_archive" and str(self.context.author.id) not in BotConfig.MAINTENANCE_BYPASS_USERS:
                BOT_REPLY = bot_response.get_admin_only_reply_msg()
                await self.bot_message.edit(content=BOT_REPLY)
                self.datetime = datetime.now() 
                latest_guild_commands[self.context.guild.id] = self
                return

            if self.command != "features":
                # Send Command to API
                data = { "command": self.command }
                response = send_to_api(data)
    
                # Response will be none if it was unsuccessful
                if response is None:
                    BOT_REPLY = bot_response.api_err_msg()
                else:
                    MC_SERVER_STATUS = response.json().get("STATUS", bot_response.api_err_msg())
                    COMMAND = response.json().get("COMMAND")

                    BOT_REPLY = bot_response.msg(COMMAND, MC_SERVER_STATUS)
            else:
                BOT_REPLY = BotConfig.HELP_MESSAGES["features"]

            # Log Bot Reply
            self.logger.info(f"BOT_REPLY: {BOT_REPLY}")

            # Inform User of their commands status
            await self.bot_message.edit(content=BOT_REPLY)

            # Update the datetime after executing the command
            self.datetime = datetime.now() 

            latest_guild_commands[self.context.guild.id] = self
        except Exception as e:
            self.logger.exception(str(e))
            await self.on_error(str(e))

    async def on_error(self, error_message):
        if self.bot_message:
            await self.bot_message.edit(content=f"Error: \n{error_message}")
        else:
            await self.context.send(f"Error: \n{error_message}")

    def _check_maintenance(self):
        """
        Maintenance Mode - Only allow Admins to use Discord bot while maintenance mode is ON.
        """
        if BotConfig.ENABLE_MAINTENANCE and str(self.context.author.id) not in BotConfig.MAINTENANCE_BYPASS_USERS:
            BOT_REPLY = bot_response.get_maintenance_msg()
            await self.bot_message.edit(content=BOT_REPLY)
            self.datetime = datetime.now() 
            latest_guild_commands[self.context.guild.id] = self
            return        