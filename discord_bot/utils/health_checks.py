import os
import requests
from requests.exceptions import RequestException, Timeout
from .logger import setup_logging
from utils.api_helper import APIUtil

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
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json(), None
        except (RequestException, Timeout, ValueError) as e:
            return None, str(e)

    def check_generic_service(self, service_name):
        data, error = self._request_status(self.base_urls[service_name])
        if error:
            return 'issues', error
        if data['status']['indicator'] == 'none':
            return "healthy", None
        return 'issues', data['status']['description']

    def check_terraform(self):
        data, error = self._request_status(self.base_urls['Terraform_Cloud'])
        if error:
            return 'issues', error
        for component in data['components']:
            if component['name'] == "Terraform Cloud":
                if component['status'] == 'operational':
                    return "healthy", None
                return 'issues', component['status']
        return 'issues', 'Unknown error'
    
    def check_lambda_MCI(self):
        data = { "action": "PING" }
        api_helper = APIUtil(self.envs)
        response = api_helper.send_to_api(data, None, 10, 3, 1)

        response = {}
        response["STATUS"] = "PONG"
        # Returns Pong if Healthy
        if response["STATUS"] == "PONG":
            return "healthy", None
        else:
            return 'issues', "API Unavailable"

    def get_service_status(self):
        self.logger.info("HealthCheck - Querying Service Health Status...")

        checks = {
            "AWS_MCI": self.check_lambda_MCI,
            'fly_io': self.check_generic_service,
            'Discord': self.check_generic_service,
            'Github': self.check_generic_service,
            'Terraform_Cloud': self.check_terraform
        }

        for service, checker in checks.items():
            if service == "Terraform_Cloud" or service == "AWS_MCI":
                status, reason = checker()
            else:
                status, reason = checker(service)

            self.services[service] = (status, reason)
            self.logger.info(f"HealthCheck - {service} is {status}. Reason: {reason}")

        return self.services

    def retrieve_health_summary(self):
        self.get_service_status()
        issues = [f"{service} - {reason}" for service, (status, reason) in self.services.items() if status == 'issues']

        if issues:
            return f'issues - {", ".join(issues)}'
        
        return 'healthy'
    
    def get_last_status(self):
        return self.services
