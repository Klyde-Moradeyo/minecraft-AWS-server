import discord
from discord.ext import commands
from utils.logger import setup_logging

class MessageManager:
    def __init__(self):
        self.logger = setup_logging() # Setting up logger
        self.message_map = {}

    async def send_new_msg(self, channel, content):
        msg = await channel.send(content)
        self.add_message(channel.id, msg.id)
        return msg.id 
    
    async def edit_msg(self, channel, content):
        try:
            message_id = self.message_map[channel.id]
            message = await channel.fetch_message(message_id)
            await message.edit(content=content)
        except discord.NotFound:
            self.logger.info(f"Message('{message_id}') not found!")
        except discord.Forbidden:
            self.logger.info("Bot lacks permission to edit the message('{message_id}')!")
        except discord.HTTPException as e:
            self.logger.info(f"Editing Message('{message_id}') failed due to {e}")
    
    async def delete_msg(self, context, message_id):
        try:
            # Fetch the message from the current channel
            message = await context.channel.fetch_message(message_id)

            # Delete the message
            await message.delete()
            await context.send(f"Deleted message with ID: {message_id}")
        except discord.NotFound:
            await context.send(f"Could not find a message with ID: {message_id}")
        except discord.Forbidden:
            await context.send("I don't have permissions to delete this message.")
        except discord.HTTPException as e:
            await context.send(f"Failed to delete message. Error: {e}")

    def add_message(self, channel_id, message_id):
        """
        Add a message mapping. If the channel_id already exists, it'll be updated.
        """
        self.message_map[channel_id] = message_id

    def get_message(self, channel_id):
        """
        Retrieve the message name for a given channel_id. 
        Returns None if the channel_id doesn't exist.
        """
        return self.message_map.get(channel_id)

    def remove_message(self, channel_id):
        """
        Remove a message mapping by channel_id. If the channel_id doesn't exist, it'll do nothing.
        """
        if channel_id in self.message_map:
            del self.message_map[channel_id]

    def list_messages(self):
        """List all message mappings."""
        return self.message_map
    
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

        return message_content.strip()  # Remove any extra newline at the end

