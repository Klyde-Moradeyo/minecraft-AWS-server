import discord
from config import *
from utils.logger import setup_logging
from utils.state_manager import StateManager

class ChannelManager:
    def __init__(self, category_name, channel_name):
        self.logger = setup_logging()
        self.channel_name = channel_name
        self.category_name = category_name
        self.state_manager = StateManager(CHANNEL_STATE_FILE)

        # Try and Restore State
        if self.state_manager.isStateExist():
            self.channel_mappings = self.state_manager.load_state()
        else:
            self.channel_mappings = {}

    async def create_channel(self, guild):
        # Check if channel has already been created
        category = discord.utils.get(guild.categories, name=self.category_name)
        if category is None:
            category = await guild.create_category(self.category_name)

        # Fetch the channel, create it if it doesn't exist
        channel = discord.utils.get(category.text_channels, name=self.channel_name)
        if channel is None:
            channel = await category.create_text_channel(self.channel_name)
            self.add_channel(guild.id, channel.id) 
            await channel.purge(limit=None)
            isFirstRun = True
        else:
            isFirstRun = False

        return channel, isFirstRun

    def add_channel(self, guild_id, channel_id):
        """
        Add a channel mapping. If the guild_id already exists, it'll be updated
        """
        self.channel_mappings[guild_id] = channel_id
        self.state_manager.save_state(self.list_channels()) # save state

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
            self.state_manager.save_state(self.list_channels()) # save state

    def list_channels(self):
        """
        List all channel mappings
        """
        return self.channel_mappings
        

