import json
from .logger import setup_logging
from .authorizer import Authorization

class APIEventParser:
    def __init__(self, event):
        self.logger = setup_logging() # Setting up logging
        self.body = self._parse_body(event)
        self.header = self._parse_headers(event)
        # self.isAuthorized = Authorization.check("ssm_param_name")

        # For debuging later
        print(self.parse_query_parameters(event))
        print(self.parse_path_parameters(event))

    def parse(self):
        action = self.extract_key("command")

        return {
            "action": action,
        }

    def extract_key(self, key):
        """
        Extract a specific key from the body.
        """
        value = self.body.get(key)
        if value is None:
            raise ValueError(f"Key '{key}' not found in input")
        return value 

    def _parse_body(self, event):
        """
        Parse the body of the event and return it as a dictionary.
        """
        try:
            body = event.get('body', '{}')
            return json.loads(body)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON input: {e}")
            raise ValueError(f"Invalid JSON input: {e}")

    def _parse_headers(self, event):
        """
        Extract headers from the event.
        """
        return event.get('headers', {})

    def parse_query_parameters(self, event):
        """
        Extract query string parameters from the event.
        """
        return event.get('queryStringParameters', {})

    def parse_path_parameters(self, event):
        """
        Extract path parameters from the event.
        """ 
        return event.get('pathParameters', {})
        
