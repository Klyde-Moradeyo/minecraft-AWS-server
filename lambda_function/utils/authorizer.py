import boto3
from logger import setup_logging
from ssm import SSMUtil

# Setting up logging
logger = setup_logging()

class AuthorizationError(Exception):
    pass

class Authorization:
    def __init__(self, ssm_param_name):
        self.ssm_param_name = ssm_param_name
        self.auhorization_token = None
        self._load_token_from_ssm()

    def _load_token_from_ssm(self):
        """
        Load the token from SSM Parameter Store. If loading fails, the token remains None.
        """
        try:
            self.auhorization_token = SSMUtil.get_param(self.ssm_param_name)
            logger.info("Successfully loaded token from SSM.")
        except Exception as e:
            logger.error(f"Error loading token from SSM: {e}")
            raise AuthorizationError("Failed to load authorization token.")

    def check(self, event):
        """
        Checks for the presence and correctness of an authorization token.
        """
        if not self.auhorization_token:
            raise AuthorizationError("Token not loaded. Denying access.")

        try:
            auth_header = event['headers'].get('Authorization', '').replace("Bearer ", "")
            if auth_header != self.auhorization_token:
                raise AuthorizationError("Invalid authorization token provided.")
            return True
        except KeyError:
            raise AuthorizationError("Authorization header missing in the event.")


