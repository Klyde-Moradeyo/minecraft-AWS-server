import discord
from utils.logger import setup_logging
from config import *

class PermissionManager:
    def __init__(self):
        self.logger = setup_logging() # Setting up logger
        self.admin_ids = set()  # Holds user IDs of admins
        self.owner = None # Holds to owner object
        self.admin_role = ADMIN_ROLE_NAME

    def is_admin(self, user_id: int) -> bool:
        """
        Check if a user is an admin
        """
        return user_id in self.admin_ids

    def _add_admin(self, user_id):
        """
        Add a user as an admin
        """
        self.admin_ids.add(user_id)

    def remove_admin(self, user_id: int):
        """
        Remove a user from the admin list
        """
        self.admin_ids.discard(user_id)

    def set_admin(self, guild):
        """
        Gets all members with a specific role.
        """
        role = discord.utils.get(guild.roles, name=self.admin_role)
        if role:
            ids = {member.id for member in guild.members if role in member.roles}
            self.admin_ids = ids
            self._add_admin(ids)
        else:
            self.logger.warning(f"No role found with name: {self.admin_role}")

    def is_owner(self, user_id: int) -> bool:
        """
        Check if a user is an owner
        """
        return user_id == self.owner.id 

    def set_owner(self, guild):
        """
        Set the owner of the server.
        """
        owner = guild.owner
        self._add_admin(owner.id)
        return owner

    def get_owner(self):
        """
        Gets the owner of the server.
        """
        return self.owner