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
        discord_bot_version = 1.0
        lambda_version = 2.1
        fargate_verson = 4.59
        infra_handler_version = 3.11
        return discord_bot_version, lambda_version, fargate_verson, infra_handler_version