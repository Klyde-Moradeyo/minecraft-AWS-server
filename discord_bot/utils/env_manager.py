import os
import json
from typing import Dict, Any, List
from .logger import setup_logging

class EnvironmentVariables:
    def __init__(self, print=False) -> None:
        self.logger = setup_logging() # Setting up logging
        self.REQUIRED_VARS = self.get_required_vars()
        self.configured = self.check_configuration()
        self.env_vars: Dict[str, Any] = {}
        self.SENSITIVE_VARS = ['DISCORD_TOKEN', 'GITHUB_TOKEN']
        self.print = print

    def get_required_vars(self):
        required_configs = [
                                # API Vars
                                'API_URL', # 'API_TOKEN',

                                # Discord Bot Token
                                'DISCORD_TOKEN',

                                # Minecraft Server Related Config
                                'SERVER_IP', 'SERVER_PORT',

                                # Admin Discord Users
                                'DEV_DISCORD_ACCOUNT_ID',

                                # Github
                                'GITHUB_REPO', 'GITHUB_TOKEN'
                            ]
        return required_configs

    def check_configuration(self):
        # Check for required configurations
        missing_configs = []
        for config in self.REQUIRED_VARS:
            if config not in os.environ:
                self.logger.error(f"Environment variable for '{config}' is missing!")
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
        self._verify_missing_variables()
        if self.print:
            self._log_env_variables()

        return self.env_vars
        
    def _fetch_required_variables(self) -> None:
        """
        Fetches required environment variables.
        """
        self.env_vars.update({var: os.getenv(var) for var in self.REQUIRED_VARS})

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
        self.logger.info(f"Configured Environment Variables")
        for key, value in self.env_vars.items():
            if key in self.SENSITIVE_VARS:
                self.logger.info(f"{key}: {'*' * 8}")  # Logs with masked value
            else:
                self.logger.info(f"{key}: {value}")

class MissingConfigurationException(Exception):
    """
    Raised when required environment variables are missing.
    """
    def __init__(self, missing_configs):
        super().__init__(f"Missing environment variables: {', '.join(missing_configs)}")
        self.missing_configs = missing_configs
