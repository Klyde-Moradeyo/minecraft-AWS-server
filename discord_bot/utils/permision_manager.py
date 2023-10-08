from utils.logger import setup_logging

class PermissionManager:
    def __init__(self):
        self.logger = setup_logging() # Setting up logger

        self.admin_users = set()  # Holds user IDs of admins
        self.owner_user_id = str() # Holds user ID of Discord Owner

    def is_owner(self, user_id: int) -> bool:
        """
        Check if a user is an owner
        """
        return user_id == self.owner_user_id
    
    def set_owner(self, user_id: int):
        """
        set a discord server owner as an owner
        """
        self.owner_user_id = user_id
        
        # Owner is an admin
        self.add_admin(self.owner_user_id) 

        self.logger.info(f"Server Owner Set... | ID: {self.owner_user_id}")

    def is_admin(self, user_id: int) -> bool:
        """
        Check if a user is an admin
        """
        return user_id in self.admin_users

    def add_admin(self, user_id: int):
        """
        Add a user as an admin
        """
        self.admin_users.add(user_id)

    def remove_admin(self, user_id: int):
        """
        Remove a user from the admin list
        """
        self.admin_users.discard(user_id)