# check if:
# - AWS is online
# - Discord is online
# - Terraform Cloud is Online
# - Github is Online
# - AWS lambda is functioning
# - Fargate is functioning and has a image available
# - 

import os
import logging
import requests
from .logger import setup_logging

class HealthCheck:
    def __init__(self):
        self.url = None
        
    def get_version(self):
        """
        Placeholder for version checker
        """
        discord_bot_version = None
        lambda_version = None
        fargate_verson = None
        infra_handler_version = None
        return discord_bot_version, lambda_version, fargate_verson, infra_handler_version
    
    def get_health(self):
        import random
        """
        Placeholder for health check
        """
        status = ["`HEALTHY💚`", "`MAINTENANCE🔧`", "`Issues⚠️ - [REASON] `"]
        # return random.choice(status)
        return "`HEALTHY💚`"