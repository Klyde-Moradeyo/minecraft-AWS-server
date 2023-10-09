import uuid
import discord
import functools
import logging
from inspect import signature
from discord.ext import tasks
from utils.logger import setup_logging
from utils.helpers import DateTimeManager
from utils.bot_response import BotResponse
from utils.message_manager import MessageManager

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
            await self.start_task(task_id, interval)
            return task_id
        except Exception as e:
            self.logger.exception(f"Scheduler - Exception in add_task: {e}")

    async def start_task(self, task_id, interval):
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
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in start_task: {e}")

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

    async def periodic_health_check(self):
        self.logger.info("periodic_health_check running!")
        pass

    async def reset_command_scroll(self, task_id, command_scroll_msg: MessageManager, bot_response: BotResponse, channel):
            """
            Reset command scroll after a specific interval.
            """
            try:
                # reset time
                reset_time = 5 

                # Get Message Map details
                msg_list = command_scroll_msg.list_messages()
                msg = msg_list[channel.id]
                # msg_id = msg["message_id"]
                msg_time = self.dt_manager.parse_datetime(msg['datetime'])
                msg_task_id = msg["task_id"]

                # Check if Message already has task running, if it's running do stop task
                if msg_task_id is not None and msg_task_id != task_id:
                    await self.stop_task(task_id, f"Scheduler - '{task_id}' - '{msg_task_id}' Task Already runnning")
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
            except Exception as e:
                self.logger.exception(f"Scheduler - '{task_id}' - Exception in reset_command_scroll for channel id: '{channel.id}': {e}")
                await self.stop_task(task_id, "Task Error")

    async def poll_minecraft_server_online(self):
        pass  # Implement
