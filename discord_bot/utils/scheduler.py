import uuid
import discord
import functools
from inspect import signature
from discord.ext import tasks
from utils.helpers import DateTimeManager
from utils.bot_response import BotResponse
from utils.message_manager import MessageManager
from utils.logger import setup_logging

class Scheduler:
    def __init__(self):
        self.logger = setup_logging()  # Setting up logger
        self.dt_manager = DateTimeManager()
        self.tasks = {}
        self.running_tasks = {} # keep track of running tasks by name

    def generate_task_id(self, task_name):
        return f"{task_name}_{uuid.uuid4()}"

    async def add_task(self, task_name: str, task_method, interval: int, *args):
        # Check if a task with the same name is already running
        if task_name in self.running_tasks:
            self.logger.warning(f"A task with the name '{task_name}' is already running.")
            return None

        # Check if the correct number of arguments are being passed
        sig = signature(task_method)
        num_params = max(0, len(sig.parameters) - 1)
        # +1 because task
        assert num_params == len(args), f"Incorrect number of arguments for {task_method.__name__}. Expected {num_params}, got {len(args)}"

        task_id = self.generate_task_id(task_name)
        partial_coro = functools.partial(task_method, task_id, *args)
        self.tasks[task_id] = tasks.loop(seconds=interval)(partial_coro)
        await self.start_task(task_id, interval)
        self.running_tasks[task_name] = task_id
        return task_id

    async def start_task(self, task_id, interval):
        if task_id in self.tasks:
            self.tasks[task_id].change_interval(seconds=interval)
            self.tasks[task_id].start()
            self.logger.info(f"Started Task '{task_id}' at check interval '{interval}'s")
        else:
            raise ValueError(f"No task found with id: {task_id}")

    async def stop_task(self, task_id):
        # Find the task_name by task_id (if necessary)
        task_name = None
        for name, id in self.running_tasks.items():
            if id == task_id:
                task_name = name
                break

        if task_id in self.tasks:
            self.tasks[task_id].stop()
            del self.tasks[task_id]

            if task_name:
                # Remove the task_name from running_tasks_by_name
                del self.running_tasks[task_name]
            self.logger.info(f"Stopped Task '{task_id}'")
        else:
            raise ValueError(f"No task found with id: '{task_id}'")

    async def periodic_health_check(self):
        self.logger.info(f"periodic_health_check running!")
        pass

    async def reset_command_scroll(self, task_id, command_scroll_msg: MessageManager, bot_response: BotResponse, channel, reset_time):
        """
        Processes Command Scroll's message map to check if the time of a specific message ID has passed a certain interval.
        """
        try:
            self.logger.info(f"Scheduler - '{task_id}' - Running Command Scroll Check for channel id: '{channel.id}'")
            current_time_str = self.dt_manager.get_current_datetime()
            dt_current_time = self.dt_manager.parse_datetime(current_time_str)
            check_interval = self.dt_manager.get_time_delta(seconds=reset_time)

            msg_list = command_scroll_msg.list_messages()
            msg = msg_list[channel.id]
            msg_time = self.dt_manager.parse_datetime(msg['datetime'])

            if msg_time < dt_current_time - check_interval:
                self.logger.info(f"Resetting command for message_id '{msg['message_id']}' in channel '{channel.id}'")
                message = bot_response.get_cmd_scroll_msg()
                await command_scroll_msg.edit_msg(channel, message)
                await self.stop_task(task_id)
                self.logger.info(f"Scheduler - '{task_id}' - Stopped reset_command_scroll for channel id: '{channel.id}'")
        except Exception as e:
            self.logger.exception(f"Scheduler - '{task_id}' - Exception in reset_command_scroll for channel id: '{channel.id}': {e}")
            await self.stop_task(task_id)
            self.logger.exception(f"Scheduler - '{task_id}' - Stopped reset_command_scroll for channel id: '{channel.id}': {e}")

    async def poll_minecraft_server_online(self):
        # Implement
        pass

# await self.scheduler.start_task("reset_command_scroll", 3600, message_id)
# await self.scheduler.start_task("poll_minecraft_server_online", 300, ip, port)
