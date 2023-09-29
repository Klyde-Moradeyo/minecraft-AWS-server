import os
import json
from typing import Dict, Any, List
from .logger import setup_logging

class EnvironmentVariables:
    def __init__(self, action) -> None:
        self.configured = self.check_configuration()
        self.env_vars: Dict[str, Any] = {}
        self.action = action
        self.logger = setup_logging() # Setting up logging

    def check_configuration(self):
        # Check for required configurations
        required_configs = List[str] = [
        # Minecraft Specific Env Vars
        'MC_PORT', 'MC_SERVER_IP', 

        # Fargate Specific Env Vars
        'CLUSTER', 'CONTAINER_NAME',  'SUBNET_ID', 'SECURITY_GROUP_ID', 'TASK_DEFINITION_NAME',

        # Terraform Cloud
        'TF_USER_TOKEN',

        # JOB to run
        'BOT_COMMAND_NAME',
        
        # Git
        'GIT_PRIVATE_KEY', 
        
        # EC2 SSH Access
        'EC2_PRIVATE_KEY'
        ]

        missing_configs = []
        for config in required_configs:
            if config not in os.environ:
                self.logger.error(f"Environment variable for {config} is missing!")
                missing_configs.append(config)
                
        if missing_configs:
            raise MissingConfigurationException(missing_configs)
        else:
            self.logger.info("All configurations are set!")

    def get_vars(self) -> Dict[str, Any]:
        """
        Fetches and decodes the environment variables. Returns the fetched variables.
        """
        self._fetch_required_variables()
        self._decode_tags_json()
        self._verify_missing_variables()
        self._log_env_variables()

        return self.env_vars
        
    def _fetch_required_variables(self) -> None:
        """
        Fetches required environment variables.
        """
        self.env_vars.update({var: os.getenv(var) for var in self.REQUIRED_VARS})

    def _decode_tags_json(self) -> None:
        """
        Decodes the TAGS_JSON environment variable and updates env_vars.
        """
        tags_json = os.getenv('TAGS_JSON')
        if not tags_json:
            raise ValueError("Missing environment variable: TAGS_JSON")

        try:
            tags = json.loads(tags_json)
        except json.JSONDecodeError:
            raise ValueError("Error decoding TAGS_JSON. Ensure it's a valid JSON string.")

        self.env_vars.update({
            'TAG_NAME': tags.get('Name'),
            'TAG_NAMESPACE': tags.get('Namespace'),
            'TAG_ENVIRONMENT': tags.get('Stage'),
            'TAG_RUNNING_COMMAND': self.action
        })

    def _verify_missing_variables(self) -> None:
        """
        Checks and raises an error if any required environment variable is missing.
        """
        missing_vars = [key for key, value in self.env_vars.items() if value is None]
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

    def _log_env_variables(self) -> None:
        """
        Logs the environment variables.
        """
        self.logger.debug(f"Configured Environment Variables")
        for key, value in self.env_vars.items():
            self.logger.debug(f"{key}: {value}")

class MissingConfigurationException(Exception):
    """
    Raised when required environment variables are missing.
    """
    def __init__(self, missing_configs):
        super().__init__(f"Missing environment variables: {', '.join(missing_configs)}")
        self.missing_configs = missing_configs
