import boto3
from .logger import setup_logging

class SSMUtil:
    def __init__(self):
        self.client = boto3.client('ssm')
        self.logger = setup_logging() # Setting up logging

    def send_param(self, command: str, type: str, ssm_path: str) -> None:
        self.client.put_parameter(
            Name=ssm_path,
            Value=command,
            Type=type,
            Overwrite=True
        )

    def get_param(self, ssm_path: str) -> str:
        response = self.client.get_parameter(Name=ssm_path, WithDecryption=True)
        value = response["Parameter"]["Value"]
        logger.debug(f"Retrieved from SSM Parameter Store: '{value}'")
        return value