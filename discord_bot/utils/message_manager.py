import discord
from discord.ext import commands

class MessageManager:
    def __init__(self):
        self.message_map = {}

    async def send_new_msg(self, channel, content):
        msg = await channel.send(content)
        self.message_map.add_message(channel.id, msg.id)
        return msg.id 
    
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

