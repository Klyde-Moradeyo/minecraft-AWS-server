import discord
from discord.ext import tasks
from .logger import setup_logging

class Scheduler:
    def __init__(self):
        self.logger = setup_logging()  # Setting up logger
        self.tasks = {
            "reset_command_scroll": tasks.loop(seconds=3600)(self.reset_command_scroll),
            "periodic_health_check": tasks.loop(seconds=300)(self.periodic_health_check)
        }

    async def start_task(self, task_name, interval):
        if task_name in self.tasks:
            self.tasks[task_name].change_interval(seconds=interval)
            self.tasks[task_name].start()
            self.logger.info(f"Started Task '{task_name}' at check interval '{interval}'s")
        else:
            raise ValueError(f"No task found with name: {task_name}")
    
    async def stop_task(self, task_name):
        if task_name in self.tasks:
            self.tasks[task_name].stop()
            self.logger.info(f"Stopped Task '{task_name}'")
        else:
            raise ValueError(f"No task found with name: '{task_name}'")

    async def periodic_health_check(self):
        self.logger.info(f"TEST - periodic_health_check running!")
        pass

    async def reset_command_scroll(self):
        # Implement
        pass

    async def poll_minecraft_server_online(self):
        # Implement
        pass
