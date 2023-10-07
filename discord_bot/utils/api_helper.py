import os
import logging
import requests
from .logger import setup_logging

class APIUtil:
    def __init__(self):
        self.url = os.getenv('API_URL')
        if self.url is None:
            logging.error("API_URL is not set in the environment variables")

    def send_to_api(self, data):
        """
        Sends data to the API and returns the response
        """
        command_url = f"{self.url}/command"
        headers = {'Content-Type': 'application/json'}

        logging.info(f"Sending Data to API: {data}")

        try:
            response = requests.post(command_url, headers=headers, json=data)
            response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx

            logging.info(f"Data: {data} \nResponse: \n{response.json()}")  # To print the response from the server
            return response.json()

        except requests.exceptions.RequestException as err:
            logging.error(f"Error occurred: {err}")
            return None
