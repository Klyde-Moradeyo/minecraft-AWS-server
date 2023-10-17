import os
import requests
from requests.exceptions import RequestException, Timeout
from config import *
from utils.logger import setup_logging
from utils.api_helper import APIUtil
from utils.file_helper import YamlHelper

class HealthCheck:
    def __init__(self, envs):
        self.services = {}
        self.logger = setup_logging()
        self.envs = envs
        self.base_urls = {
            'fly_io': 'https://status.flyio.net/api/v2/summary.json',
            'AWS_MCI': envs['API_URL'], # Minecraft Infrastructure Coordinator Lambda
            'Discord': 'https://discordstatus.com/api/v2/summary.json',
            'Terraform_Cloud': 'https://status.hashicorp.com/api/v2/summary.json',
            'Github': 'https://kctbh9vrtdwd.statuspage.io/api/v2/summary.json'
        }

    def _request_status(self, url):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            return response.json(), None
        except (RequestException, Timeout, ValueError) as e:
            return None, str(e)

    def check_generic_service(self, service_name):
        data, error = self._request_status(self.base_urls[service_name])
        if error:
            return False, error
        if data['status']['indicator'] == 'none':
            return True, None
        return False, data['status']['description']

    def get_service_status(self):
        self.logger.info("HealthCheck - Querying Service Health Status...")

        checks = {
            # "AWS_MCI": self._check_lambda_MCI,
            'fly_io': self._check_flyio,
            'Discord': self._check_discord,
            'Github': self._check_github,
            'Terraform_Cloud': self._check_terraform
        }

        for service, checker in checks.items():
            status, reason = checker()

            self.services[service] = (status, reason)
            self.logger.info(f"HealthCheck - {service} is {status}. Reason: {reason}")

        return self.services

    def retrieve_health_summary(self, bot_msg_yaml: YamlHelper):
        self.get_service_status()
        issues = [f"{service} - {reason}" for service, (status, reason) in self.services.items() if status == False]

        if issues:
            issue_details = { "ISSUE_DETAILS": f"{', '.join(issues)}"}
            bot_msg_yaml.resolve_placeholders(issue_details)
            return bot_msg_yaml.get_data()["INFRASTRUCTURE_STATUS_MSG"]["ISSUES"]
        
        return bot_msg_yaml.get_data()["INFRASTRUCTURE_STATUS_MSG"]["HEALTHY"]
    
    def check_maintenance_mode(self):
        return "WIP"
    
    def get_last_status(self):
        return self.services
    
    def _check_flyio(self):
        components_list = [ "Deployments", "LHR - London, United Kingdom", "Persistent Storage (Volumes)" ] # components to check
        data, error = self._request_status(self.base_urls["fly_io"])
        if error:
            return False, error
        for component in data['components']:
            if component['name'] in components_list:
                if component['status'] == 'operational':
                    return True, None
                return False, component['status']
        return False, 'Unknown error'
    
    def _check_lambda_MCI(self):
        """
        Checks the health of the Lambda MCI component by sending a PING request.
        """
        data = { "action": "PING" }

        try:
            api_helper = APIUtil(self.envs)
            response = api_helper.send_to_api(data, "Health Check")

            # Check if the response indicates that the component is healthy
            if response and response["STATUS"] == "PONG":
                return True, None
            else:
                return False, "Core Component MCI is not Operational"

        except Exception as e:
            return False, f"Failed to check Lambda MCI: '{str(e)}'"

    def _check_discord(self):
        return self.check_generic_service("Discord")

    def _check_terraform(self):
        components_list = [ "Terraform Cloud" ] # components to check
        data, error = self._request_status(self.base_urls["Terraform_Cloud"])
        if error:
            return False, error
        for component in data['components']:
            if component['name'] in components_list:
                if component['status'] == 'operational':
                    return True, None
                return False, component['status']
        return False, 'Unknown error'

    def _check_github(self):
        components_list = [ "Git Operations" ] # components to check
        data, error = self._request_status(self.base_urls["Github"])
        if error:
            return False, error
        for component in data['components']:
            if component['name'] in components_list:
                if component['status'] == 'operational':
                    return True, None
                return False, component['status']
        return False, 'Unknown error'
