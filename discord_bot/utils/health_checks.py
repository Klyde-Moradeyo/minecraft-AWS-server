# check if:
# - AWS is online
# - Discord is online
# - Terraform Cloud is Online
# - Github is Online
# - AWS lambda is functioning
# - Fargate is functioning and has a image available
# - 

import os
import requests
from requests.exceptions import RequestException
from .logger import setup_logging

class HealthCheck:
    def __init__(self):
        self.services = None
        self.logger = setup_logging()

    def get_service_status(self):
        self.logger.info("HealthCheck - Querying Service Health Status...")
        services = {
                    "AWS_MCI_Lambda": self._check_AWS_MCI, # Minecraft Infrastructure Coordinator Lambda # use aws health and a ping pong for lambda
                    'fly_io': self._check_flyio,
                    'Discord': self._check_discord,
                    'Terraform_Cloud': self._check_terraform,
                    'Github': self._check_github,
        }
        self.logger.info(f"HealthCheck - Received Service Health Status:'{services}'")   
        return services

    def retrieve_health_summary(self):
        self.services = self.get_service_status()
        issues = []
        for service, checker in self.services.items():
            status, reason = checker()
            if status == 'issues':
                issues.append(f"{service} - {reason}")

        if issues:
            return f'issues - {", ".join(issues)}'
        
        return 'healthy'
    
    def get_last_status(self):
        return self.services

    def _check_flyio(self):
        self.logger.info("HealthCheck - Retrieving Fly.io Status...")
        url = 'https://status.flyio.net/api/v2/summary.json'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['status']['indicator'] == 'none':
                return 'healthy', ''
            return 'issues', data['status']['description']
        except RequestException as e:
            return 'issues', str(e)

    def _check_aws(self):
        self.logger.info("HealthCheck - Retrieving AWS Status...")
        url = 'https://status.aws.amazon.com/api/v2/summary.json'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['status']['indicator'] == 'none':
                return 'healthy', ''
            return 'issues', data['status']['description']
        except RequestException as e:
            return 'issues', str(e)

    def _check_discord(self):
        self.logger.info("HealthCheck - Retrieving Discord Status...")
        url = 'https://discordstatus.com/api/v2/summary.json'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['status']['indicator'] == 'none':
                return 'healthy', ''
            return 'issues', data['status']['description']
        except RequestException as e:
            return 'issues', str(e)

    def _check_terraform(self):
        self.logger.info("HealthCheck - Retrieving Terraform Cloud Status...")
        url = "https://status.hashicorp.com/api/v2/summary.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            for component in data['components']:
                if component['name'] == "Terraform Cloud":
                    if component['status'] == 'operational':
                        return 'healthy', ''
                    return 'issues', component['status']
        except RequestException as e:
            return 'issues', str(e)

    def _check_github(self):
        self.logger.info("HealthCheck - Retrieving Github Status...")
        url = 'https://kctbh9vrtdwd.statuspage.io/api/v2/summary.json'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['status']['indicator'] == 'none':
                return 'healthy', ''
            return 'issues', data['status']['description']
        except RequestException as e:
            return 'issues', str(e)
