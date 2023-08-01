import random

class Bot_Response:
    def __init__(self):
        help_desk_users = "`@The Black Mango`"

        self.STARTING_REPLIES = [
            "Your Minecraft server is under construction! Please hang in there, it should be ready in about 6-7 minutes.",
            "We're hard at work setting up your Minecraft server. Expect to be playing in just 6-7 minutes!",
            "Minecraft server coming up! Sit tight, we'll have it ready for you in roughly 6-7 minutes."
        ]

        self.ACTIVATING_REPLIES = [
            "Initiating server setup. Your Minecraft world is being created!",
            "Hang tight! We're in the process of creating your Minecraft world.",
            "Just a moment more. We're bringing your Minecraft server to life!"
        ]

        self.RUNNING_REPLIES = [
            "Your Minecraft server is being prepared. Please wait while we set up the infrastructure for your adventure!",
            "Great news! We're currently setting up your Minecraft server. Get ready to embark on your journey soon!",
            "Your Minecraft server is currently being provisioned. It won't be long before you can start your exciting adventure!"
        ]

        self.STOPPING_REPLIES = [
            "We're wrapping up server setup. Your Minecraft world is almost ready!",
            "Just a few final touches and your Minecraft world will be ready.",
            "Almost there! Your Minecraft world is nearly ready for you."
        ]

        self.STOPPED_REPLIES = [
            "Minecraft server setup complete. Welcome to your new world!",
            "Server setup is done! Your Minecraft world awaits.",
            "All done! Your Minecraft server is ready for exploration."
        ]

        self.STOP_PROVISIONING_REPLIES = [
            "We're preparing to take your Minecraft server offline, please wait.",
            "Starting the shutdown process for your Minecraft server, please hold on.",
            "We're beginning the process to bring your Minecraft server offline."
        ]

        self.STOP_ACTIVATING_REPLIES = [
            "Initiating server shutdown. Your Minecraft world is being saved.",
            "Starting the process to safely shut down your Minecraft world.",
            "Your Minecraft server is preparing to go offline. We're saving your world data."
        ]

        self.STOP_RUNNING_REPLIES = [
            "Your Minecraft server is currently shutting down.",
            "Server shutdown in progress. Your Minecraft world will be ready for you when you return.",
            "Your Minecraft server is on its way offline. We're making sure everything is saved for next time."
        ]

        self.API_ERROR_MSGS = [
            f"Oh no! There seems to be a creeper in the system. Please try again and if the problem persists, get in touch with {help_desk_users}.",
            f"We hit some bedrock! Your request couldn't be completed right now. If you continue to have issues, let {help_desk_users} know.",
            f"It seems our redstone circuitry is acting up. Please try again and let {help_desk_users} know if you're still facing issues.",
        ]

        self.MC_SERVER_UP = [
            "✅ Great news! Our Minecraft server has returned from its break and is ready for crafting and building. Time to dive back in!",
            "✅ Get your pickaxes ready! The server is online and eager for more Minecraft adventures.",
            "✅ All systems are go! Our server has returned from the Nether and is now online. It's crafting time once again.",
            "✅ Attention all builders! The Minecraft server is now online and ready for your epic adventure.",
            "✅ We're back! The Minecraft server has returned from its ocean monument adventure. Dive back into your world!"
        ]

        self.MC_SERVER_DOWN = [
            "🚫 Minecraft server is currently taking a well-earned break. Type `!start` to launch the server!",
            "🚫 The Minecraft server is currently offline. Now's a great time to plan your next big build.",
            "🚫 Our server is currently catching some Z's. Type `!start` to nudge it awake for more crafting.",
            "🚫 The Minecraft server is off on a short adventure. Type `!start` for its return, and be ready for more epic gameplay!",
            "🚫 The Minecraft server is currently in rest mode. A perfect opportunity to gather your thoughts for your next big project!"
        ]

        self.COMMAND_SCROLL = [
            "📜 The command scroll is at your service 🔮",
            "📜 Scroll open, awaiting command 🌟",
            "📜 Input command to start the magic 🔮",
            "🔮 Ready and waiting for your command 📜",
        ]

        self.MAINTENANCE_MESSAGES = [
            "⚙️ Minecraft server maintenance underway. Back shortly!",
            "⚙️ We're tinkering behind the scenes. Be right back!",
            "⚙️ Crafting break! Maintenance in progress.",
            "⚙️ Temporarily offline for upgrades.",
            "⚙️ Server enhancements in motion. See you soon!",
            "⚙️ Leveling up! Momentary downtime.",
            "⚙️ Brb - Server maintenance ongoing.",
            "⚙️ Minecraft world undergoing care. Back shortly!",
            "⚙️ Redstone check-in progress. Be back soon!",
            "⚙️ Hold tight! Maintenance mode activated."
        ]

    def msg(self, command, state):
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

        return bot_reply

    def api_err_msg(self):   
        return random.choice(self.API_ERROR_MSGS)
    
    def get_cmd_scroll_msg(self):
        return random.choice(self.COMMAND_SCROLL)
    
    def get_maintenance_msg(self):
        return random.choice(self.MAINTENANCE_MESSAGES)