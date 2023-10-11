import discord
from discord.ext import commands
from config import *
from utils.logger import setup_logging
from utils.helpers import DateTimeManager
from utils.state_manager import StateManager

class MessageManager:
    def __init__(self, state_file="NOT_SPECIFIED"):
        self.logger = setup_logging()
        self.datetime = DateTimeManager()
        self.state_manager = StateManager(state_file)

        # Try and Restore State
        if self.state_manager.has_data():
            self.message_map = self.state_manager.get_state()
            self.logger.info(f"MessageHandler State('{state_file}'): {self.message_map}")
        else:
            self.message_map = {}

    async def send_new_msg(self, channel, content):
        if channel.id in self.message_map:
            await self.edit_msg(channel, content)
            return self.get_message_id(channel.id)
        else:
            msg = await channel.send(content)
            self.add_message(channel.id, msg.id)
            return msg.id
    
    async def edit_msg(self, channel, content):
        try:
            message_info = self.message_map.get(channel.id)
            if message_info is None:
                self.logger.info(f"No message found for channel {channel.id}")
                return

            message_id = message_info['message_id']
            message = await channel.fetch_message(message_id)
            self.logger.info(f"msg_id: '{message_id}' - Updating message")
            await message.edit(content=content)
            # Update datetime when the message is edited
            self.update_message_datetime(channel.id)
        except discord.NotFound:
            self.logger.info(f"msg_id: '{message_id}' - Message not found!")
        except discord.Forbidden:
            self.logger.info(f"msg_id: '{message_id}' - Bot lacks permission to edit the message!")
        except discord.HTTPException as e:
            self.logger.info(f"msg_id: '{message_id}' -  Editing Message failed due to {e}")

    async def delete_msg(self, context, message_id):
        try:
            # Fetch the message from the current channel
            message = await context.channel.fetch_message(message_id)

            # Delete the message
            await message.delete()
            await context.send(f"msg_id: '{message_id}' - Deleted message")
        except discord.NotFound:
            await context.send(f"msg_id: '{message_id}' - Could not find a message")
        except discord.Forbidden:
            await context.send(f"msg_id: '{message_id}' - I don't have permissions to delete this message.")
        except discord.HTTPException as e:
            await context.send(f"msg_id: '{message_id}' - Failed to delete message. Error: {e}")

    def add_message(self, channel_id, message_id, task_id=None):
        """
        Add a message mapping. If the channel_id already exists, it'll be updated.
        """
        self.message_map[channel_id] = {
            'message_id': message_id,
            'datetime': self.datetime.get_current_datetime(),
            'task_id': task_id
        }

        # Update state
        self.state_manager.save_state(self.list_messages())

    async def get_message(self, channel):
        """
        Retrieve the message object for a given channel.
        Returns None if the channel_id doesn't exist in message_map
        or if the message doesn't exist in the channel.
        """
        # Get the message info from the message_map dictionary
        message_info = self.message_map.get(channel.id)

        if message_info is None:
            return None

        message_id = message_info['message_id']  # Access message_id from message_info

        # Use channel.fetch_message to get the message object
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            return None
        except discord.HTTPException as e:
            # Handle other HTTP exceptions (e.g., lack of permissions, rate limits, etc.)
            self.logger.info(f"'msg_id: '{message_id}' - Failed to fetch message: {e}")
            return None

        return message
    
    def get_message_id(self, channel_id):
        """
        Get message id
        """
        message_info = self.message_map.get(channel_id)
        if message_info is None:
            return None
        return message_info['message_id']
    
    def get_message_datetime(self, channel):
        """
        Retrieve the datetime for a given channel's message.
        Returns None if the channel_id doesn't exist in message_map.
        """
        message_info = self.message_map.get(channel.id)
        if message_info is None:
            return None
        return message_info['datetime']

    def remove_message(self, channel_id):
        """
        Remove a message mapping by channel_id. If the channel_id doesn't exist, it'll do nothing.
        """
        if channel_id in self.message_map:
            del self.message_map[channel_id]
            self.state_manager.save_state(self.list_messages()) # Update state 

    def has_message(self, channel_id):
        """
        Check if a specific channel has a message mapped to it.
        
        :param channel_id: ID of the channel to check.
        :return: True if the channel has a message mapped, otherwise False.
        """
        return channel_id in self.message_map

    def list_messages(self):
        """
        List all message mappings.
        """
        return self.message_map
    
    def update_message_datetime(self, channel_id):
        """
        Update the datetime for a given channel_id.
        """
        message_info = self.message_map.get(channel_id)
        if message_info:
            message_info['datetime'] = self.datetime.get_current_datetime()
        
        # Update state
        self.state_manager.save_state(self.list_messages())

    def update_task_id(self, channel_id, task_id):
        """
        Update the task_id for a given channel_id.
        """
        message_info = self.message_map.get(channel_id)
        if message_info:
            message_info['task_id'] = task_id

        # Update state
        self.state_manager.save_state(self.list_messages())
    
    def construct_message_from_dict(self, data):
        """
        Construct a message from the provided YAML data and placeholders.
        """
        message_content = ""

        # Helper function to process each value based on its type
        def process_value(value):
            if isinstance(value, list):
                return "\n".join(map(process_value, value))
            elif isinstance(value, dict):
                return "\n".join([f"{k}: {process_value(v)}" for k, v in value.items()])
            else:
                return value

        # If the data is a list, process each item in the list
        if isinstance(data, list):
            message_content += "\n".join(map(process_value, data))
        else:
            # Append HEADER if exists
            if 'HEADER' in data:
                message_content += process_value(data['HEADER']) + "\n"

            # Dynamically process other keys excluding HEADER and FOOTER
            for key, value in data.items():
                if key not in ['HEADER', 'FOOTER']:
                    message_content += process_value(value) + "\n"

            # Append FOOTER if exists
            if 'FOOTER' in data:
                message_content += process_value(data['FOOTER'])

        return message_content.strip() # Remove any extra newline at the end