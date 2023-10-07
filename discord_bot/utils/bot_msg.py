import random
import discord

class BotMsg():
    def __init__(self, channel_id):
        self.msg_id = {}
        
        help_desk_users = "REPLACE"

    async def send_new_msg(self, msg, channel_id):
        msg = await channel.send(help_message_content)
        return msg.id 
    
        
    def cmd_reply(self, command, state):
        if state == "MC_SERVER_UP":
            bot_reply = random.choice(self.MC_SERVER_UP)
        elif state == "MC_SERVER_DOWN":
            bot_reply = random.choice(self.MC_SERVER_DOWN)
        elif command == "start":
            if state in ["PROVISIONING", "PENDING"]:
                bot_reply = random.choice(self.STARTING_REPLIES)
            elif state == "ACTIVATING":
                bot_reply = random.choice(self.ACTIVATING_REPLIES)
            elif state == "RUNNING":
                bot_reply = random.choice(self.RUNNING_REPLIES)
            elif state in ["DEACTIVATING", "STOPPING"]:
                bot_reply = random.choice(self.STOPPING_REPLIES)
            elif state == "STOPPED":
                bot_reply = random.choice(self.STOPPED_REPLIES)
            else:
                bot_reply = "Hmm, we're not sure what's happening. Please check back soon."
        elif command == "stop":
            if state in ["PROVISIONING", "PENDING"]:
                bot_reply = random.choice(self.STOP_PROVISIONING_REPLIES)
            elif state == "ACTIVATING":
                bot_reply = random.choice(self.STOP_ACTIVATING_REPLIES)
            elif state == "RUNNING":
                bot_reply = random.choice(self.STOP_RUNNING_REPLIES)
            else:
                bot_reply = "Hmm, we're not sure what's happening. Please check back soon."
        elif command == "mc_world_archive":
            bot_reply = random.choice(self.WORLD_ARCHIVE_REPO_REPLIES)
        else:
            bot_reply = f"Bot Reply not configured for command '{command}'"

        return bot_reply

    def api_err_msg(self):   
        return random.choice(self.API_ERROR_MSGS)
    
    def get_cmd_scroll_msg(self):
        return random.choice(self.COMMAND_SCROLL)
    
    def get_maintenance_msg(self):
        return random.choice(self.MAINTENANCE_MESSAGES)
    
    def get_admin_only_reply_msg(self):
        return random.choice(self.ADMIN_ONLY_REPLIES)