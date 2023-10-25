import random
from utils.message_manager import MessageManager
from utils.logger import setup_logging

class BotResponse():
    def __init__(self, data):
        self.logger = setup_logging()
        self.data = data
        self.help_desk_users = "REPLACE"

    def cmd_reply(self, command, state):
        if state == "MC_SERVER_UP":
            bot_reply = self.get_server_running_msg()
        elif state == "MC_SERVER_DOWN":
            bot_reply = random.choice(self.data["MINECRAFT_SERVER"]["MC_SERVER_DOWN"])
        elif command == "start":
            if state in ["PROVISIONING", "PENDING"]:
                bot_reply = random.choice(self.data["FARGATE"]["STARTING_REPLIES"])
            elif state == "ACTIVATING":
                bot_reply = random.choice(self.data["FARGATE"]["ACTIVATING_REPLIES"])
            elif state == "RUNNING":
                bot_reply = random.choice(self.data["FARGATE"]["RUNNING_REPLIES"])
            elif state in ["DEACTIVATING", "STOPPING"]:
                bot_reply = random.choice(self.data["FARGATE"]["STOPPING_REPLIES"])
            elif state == "STOPPED":
                bot_reply = random.choice(self.data["FARGATE"]["STOPPED_REPLIES"])
            else:
                bot_reply = "Hmm, we're not sure what's happening. Please check back soon."
        elif command == "stop":
            if state in ["PROVISIONING", "PENDING"]:
                bot_reply = random.choice(self.data["FARGATE"]["STOP_PROVISIONING_REPLIES"])
            elif state == "ACTIVATING":
                bot_reply = random.choice(self.data["FARGATE"]["STOP_ACTIVATING_REPLIES"])
            elif state == "RUNNING":
                bot_reply = random.choice(self.data["FARGATE"]["STOP_RUNNING_REPLIES"])
            else:
                bot_reply = "Hmm, we're not sure what's happening. Please check back soon."
        elif command == "mc_world_archive":
            bot_reply = random.choice(self.data["ARCHIVING_ACTIONS"]["WORLD_ARCHIVE_REPO_REPLIES"])
        else:
            bot_reply = f"Bot Reply not configured for command '{command}'"

        return bot_reply

    def api_err_msg(self):   
        return random.choice(self.data["ERRORS_AND_MAINTENANCE"]["API_ERROR_MSGS"])
    
    def get_cmd_scroll_msg(self):
        return random.choice(self.data["COMMAND_SCROLL"]["READY"])
    
    def get_disabled_cmd_scroll_msg(self):
        return random.choice(self.data["COMMAND_SCROLL"]["DISABLED"])
    
    def get_maintenance_msg(self):
        return random.choice(self.data["ERRORS_AND_MAINTENANCE"]["MAINTENANCE_MESSAGES"])
    
    def get_admin_only_reply_msg(self):
        return random.choice(self.data["ACCESS_RESTRICTIONS"]["ADMIN_ONLY_REPLIES"])
    
    def get_server_running_msg(self):
        return random.choice(self.data["MINECRAFT_SERVER"]["MC_SERVER_UP"])
    
    def get_features(self):
        return MessageManager().construct_message_from_dict(self.data["FEATURES"])