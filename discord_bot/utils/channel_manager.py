import discord
from utils.logger import setup_logging

class ChannelManager:
    def __init__(self, category_name, channel_name):
        self.logger = setup_logging() # Setting up logger
        self.channel_mappings = {}
        self.category_name = category_name
        self.channel_name = channel_name

    async def create_channel(self, guild):
        # Fetch the category, create it if it doesn't exist
        category = discord.utils.get(guild.categories, name=self.category_name)
        if category is None:
            category = await guild.create_category(self.category_name)

        # Fetch the channel, create it if it doesn't exist
        channel = discord.utils.get(category.text_channels, name=self.channel_name)
        if channel is None:
            channel = await category.create_text_channel(self.channel_name)

        self.add_channel(guild.id, channel.id) # store channel
        return channel

    def add_channel(self, guild_id, channel_id):
        """
        Add a channel mapping. If the guild_id already exists, it'll be updated
        """
        self.channel_mappings[guild_id] = channel_id

    def get_channel(self, guild):
        """
        Retrieve the channel object for a given guild
        Returns None if the guild_id doesn't exist
        """
        channel_id = self.channel_mappings.get(guild.id)
        if channel_id is None:
            return None
        channel = guild.get_channel(channel_id)
        return channel

    def remove_channel(self, guild_id):
        """
        Remove a channel mapping by guild_id. If the guild_id doesn't exist, it'll do nothing
        """
        if guild_id in self.channel_mappings:
            del self.channel_mappings[guild_id]

    def list_channels(self):
        """
        List all channel mappings
        """
        return self.channel_mappings
        

