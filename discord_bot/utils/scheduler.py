import uuid
import discord
import functools
import logging
from inspect import signature
from discord.ext import tasks
from config import *
from utils.logger import setup_logging
from utils.helpers import DateTimeManager
from utils.bot_response import BotResponse
from utils.message_manager import MessageManager
from utils.channel_manager import ChannelManager
from utils.health_checks import HealthCheck
from utils.file_helper import YamlHelper
from utils.minecraft import MinecraftServer

class TaskNotFoundError(Exception):
    """
    Exception raised when a task is not found.
    """
    pass

class Scheduler:
    def __init__(self):
        self.logger = setup_logging()
        self.dt_manager = DateTimeManager()
        self.tasks = {}

    def _generate_task_id(self, task_name):
        return f"{task_name}_{uuid.uuid4()}"

    def _task_exists(self, task_id):
        return task_id in self.tasks

    async def add_task(self, task_name: str, task_method, interval: int, *args):
        """
        Add a new task to the scheduler.
        """
        try:
            sig = signature(task_method)
            num_params = max(0, len(sig.parameters) - 1)
            assert num_params == len(args), (f"Incorrect number of arguments for '{task_method.__name__}'. Expected '{num_params}', got '{len(args)}'")

            task_id = self._generate_task_id(task_name)
            partial_coro = functools.partial(task_method, task_id, *args)
            self.tasks[task_id] = tasks.loop(seconds=interval)(partial_coro)
            await self._start_task(task_id, interval)
            return task_id
        except Exception as e:
            self.logger.exception(f"Scheduler - Exception in add_task: {e}")

    async def _start_task(self, task_id, interval):
        """
        Start a scheduled task.
        """
        try:
            if not self._task_exists(task_id):
                raise TaskNotFoundError(f"No task found with id: {task_id}")

            self.tasks[task_id].change_interval(seconds=interval)
            self.tasks[task_id].start()
            self.logger.info(f"Scheduler - '{task_id}' - Started at check interval '{interval}s'")
        except Exception as e:
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in _start_task: {e}")

    async def stop_task(self, task_id, reason):
        """
        Stop a scheduled task.
        """
        try:
            if not self._task_exists(task_id):
                raise TaskNotFoundError(f"No task found with id: '{task_id}'")

            self.tasks[task_id].stop()
            del self.tasks[task_id]  # Remove task from the tasks dictionary
            self.logger.info(f"Scheduler - '{task_id}' - Stopped Task - Reason: {reason}")
        except Exception as e:
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in stop_task: {e}")

    async def periodic_health_check(self, task_id, health_check: HealthCheck, guilds, info_msg: MessageManager, channel_manager: ChannelManager, bot_msg_yaml: YamlHelper):
        try:
            # Get Health Status
            health_status = { "INFRASTRUCTURE_STATUS_MSG": health_check.retrieve_health_summary(bot_msg_yaml) }
            
            if bot_msg_yaml.get_variables()["INFRASTRUCTURE_STATUS_MSG"] != health_status["INFRASTRUCTURE_STATUS_MSG"]:
                self.logger.info(f"Scheduler - '{task_id}' - Updating info message with latest health status: '{health_status['INFRASTRUCTURE_STATUS_MSG']}'")

                # Prepare Message
                bot_msg_yaml.resolve_placeholders(health_status)
                message = info_msg.construct_message_from_dict(bot_msg_yaml.get_data()["USER_GUIDE"]) 

                # Update Info Section with new health status
                for guild in guilds:
                    channel = channel_manager.get_channel(guild)
                    await info_msg.edit_msg(channel, message)

            self.logger.info(f"Scheduler - '{task_id}' - Periodic Health Check Status: '{health_status['INFRASTRUCTURE_STATUS_MSG']}'")
        except Exception as e:
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in periodic_health_check: {e}")

    async def reset_command_scroll(self, task_id, command_scroll_msg: MessageManager, bot_response: BotResponse, channel, reset_time):
            """
            Reset command scroll after a specific interval.
            """
            try:
                # Get Message Map details
                msg_list = command_scroll_msg.list_messages()
                msg = msg_list[channel.id]
                # msg_id = msg["message_id"]
                msg_time = self.dt_manager.parse_datetime(msg['datetime'])
                msg_task_id = msg["task_id"]

                # Check if Message already has task running, if it's running do stop task
                if msg_task_id is not None and msg_task_id != task_id:
                    await self.stop_task(task_id, f"Task Already runnning")
                    return
                
                command_scroll_msg.update_task_id(channel.id, task_id)
                self.logger.info(f"Scheduler - '{task_id}' - Running Command Scroll Check for channel id: '{channel.id}'")

                current_time_str = self.dt_manager.get_current_datetime()
                dt_current_time = self.dt_manager.parse_datetime(current_time_str)
                check_interval = self.dt_manager.get_time_delta(seconds=reset_time)

                if msg_time < dt_current_time - check_interval:
                    self.logger.info(f"Scheduler - '{task_id}' - Resetting command for message_id '{msg['message_id']}' in channel '{channel.id}'")
                    message = bot_response.get_cmd_scroll_msg()
                    await command_scroll_msg.edit_msg(channel, message)
                    await self.stop_task(task_id, "Task Finished")
                    command_scroll_msg.update_task_id(channel.id, None)
            except Exception as e:
                self.logger.exception(f"Scheduler - '{task_id}' - Exception in reset_command_scroll for channel id: '{channel.id}': {e}")
                await self.stop_task(task_id, "Task Error")

    async def poll_minecraft_server_online(self, task_id, envs, context, info_msg: MessageManager, command_scroll_msg: MessageManager, bot_msg_yaml: YamlHelper, bot_response: BotResponse):
        try:
            server = MinecraftServer(envs["SERVER_IP"], envs["SERVER_PORT"])
            server_info = server.check()
            self.logger.info(f"poll_minecraft_server_online - Received {server_info}")

            if server_info["online"]:
                # Inform User in private dms that the server is running
                self.logger.info(f"Scheduler - '{task_id}' - Minecraft Server is Online...Sending DM '{message}'")
                message = bot_response.get_server_running_msg()
                user_message = await context.author.send(message)
                await self.add_task("reset_mc_server_online_private_msg", self.reset_mc_server_online_private_msg, RESET_PRIVATE_ONLINE_MSG_CHECK_INTERVAL, self.dt_manager.get_current_datetime(), user_message, RESET_PRIVATE_ONLINE_MSG_TIME)

                # Edit Command Scroll Message to inform users it is online
                self.logger.info(f"Scheduler - '{task_id}' - Sending Command scroll msg: '{message}'")
                message = bot_response.get_server_running_msg()
                await command_scroll_msg.edit_msg(context.channel, message)
                await self.add_task("reset_command_scroll", self.reset_command_scroll, RESET_COMMAND_SCROLL_CHECK_INTERVAL, command_scroll_msg, bot_response, context.channel, RESET_COMMAND_SCROLL_TIME)

                # Add version to info message
                self.logger.info(f"Scheduler - '{task_id}' - Update Info msg to include mc server version('{server_info['version']}')")
                version = { "SERVER_VERSION": server_info["version"] }
                bot_msg_yaml.resolve_placeholders(version)
                message = info_msg.construct_message_from_dict(bot_msg_yaml.get_data()["USER_GUIDE"]) 
                await info_msg.edit_msg(context.channel, message)

                # Stop Task from running as its finished
                await self.stop_task(task_id, "Task Finished")
        except Exception as e:
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in poll_minecraft_server_online for channel id: '{context.channel.id}': {e}")
            await self.stop_task(task_id, "Task Error")

    async def reset_mc_server_online_private_msg(self, task_id, sent_datetime, message, reset_time):
        try:
            # Convert send_datetime string to datetime object
            sent_dt = self.dt_manager.parse_datetime(sent_datetime)
        
            # Get current datetime
            current_dt = self.dt_manager.parse_datetime(self.dt_manager.get_current_datetime())

            # Check if X Seconds have passed since send_datetime
            if current_dt - sent_dt >= self.dt_manager.get_time_delta(seconds=reset_time):
                self.logger.info(f"Scheduler - '{task_id}' - msg_id: '{message.id}' - Deleting private msg")
                await message.delete()
                # Stop Task from running as its finished
                await self.stop_task(task_id, "Task Finished")
        except Exception as e:
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in reset_mc_server_online_private_msg for' {message.id}': {e}")
            await self.stop_task(task_id, "Task Error")
          
    async def check_if_channel_is_present(self):
        pass  # Implement

    async def purge_non_bot_messages(self, task_id, channel: discord.TextChannel, bot_user):
        """
        Purge all messages in the given channel that aren't sent by the bot.
        """
        await channel.purge(check=lambda msg: msg.author != bot_user)

