from config import *
from .logger import setup_logging
from .message_manager import MessageManager
from .permision_manager import PermissionManager
from .api_helper import APIUtil
from .bot_response import BotResponse

class ProcessAPICommand:
    ADMIN_ONLY_COMMANDS = ["mc_world_archive"]
    def __init__(self, context, command, envs, command_scroll_msg: MessageManager, permision_manager: PermissionManager, bot_response: BotResponse):
        self.logger = setup_logging()
        self.context = context
        self.command = command
        self.command_scroll_msg = command_scroll_msg
        # self.datetime = datetime.now()
        self.bot_response = bot_response
        self.permision_manager = permision_manager
        self.envs = envs

    async def execute(self):
        self.logger.info(f"Proccessing Command: '{self.command}'")
        try:
            # If bot is not done initilizing, do nothing
            if not READY:
                return
            
            message = f"User {self.context.author.name} used `{self.command}` command..."
            await self.command_scroll_msg.edit_msg(self.context.channel, message)

            # If user is not authroized to run the command then return
            if not await self._authorized():
                return

            data = self._create_data()
            api = APIUtil(self.envs)
            reason = f"Discord User used command: '{self.command}'"
            response = api.send_to_api(data, reason)

            # Response will be none if it was unsuccessful
            self.logger.info(f"API Response: {response}")
            if response is None:
                message = self.bot_response.api_err_msg()
            else:
                mc_server_status = response.get("STATUS")
                command = response.get("COMMAND")
                message = self.bot_response.cmd_reply(command, mc_server_status) 

            # Send new message
            await self.command_scroll_msg.edit_msg(self.context.channel, message)
            self.logger.info(message)
        except Exception as e:
            self.logger.exception(str(e))
            await self.on_error(str(e))
 
    async def on_error(self, error_message):
        await self.command_scroll_msg.edit_msg(self.context.channel, error_message)

    def _create_data(self):
        data = {
            "action": self.command,
            "user": {
                "id": str(self.context.author.id),
                "username": str(self.context.author.name),
                # "role": "normal"
            },
            "discord_server": {
                "id": str(self.context.guild.id),
                "name": str(self.context.guild.name),
            },
            # "mc_server_settings": {
            #     "id": "unknown-id",
            #     "name": "UnknownServer",
            #     "version": "latest",
            #     "mods": []
            # },
        }

        return data
    
    async def _authorized(self):
        """
        Authrozier to check if User get use a command
        """
        # Check Maintenance - Only allow Admins to use Discord bot while maintenance mode is ON.
        self.logger.info(f"IS_MAINTENANCE: {IS_MAINTENANCE}")
        if IS_MAINTENANCE and not self.permision_manager.is_admin(self.context.author.id):
            message = self.bot_response.get_maintenance_msg()
            await self.command_scroll_msg.edit_msg(self.context.channel, message)
            # self.datetime = datetime.now() 
            # latest_guild_commands[self.context.guild.id] = self
            return False
        
        if self.command in self.ADMIN_ONLY_COMMANDS and not self.permision_manager.is_admin(self.context.author.id):
            self.logger.info(f"{self.context.author.name} not AUTHORIZED to perform {self.command}")
            message = self.bot_response.get_admin_only_reply_msg()
            await self.command_scroll_msg.edit_msg(self.context.channel, message)
            # self.datetime = datetime.now() 
            # latest_guild_commands[self.context.guild.id] = self
            return False

        return True
