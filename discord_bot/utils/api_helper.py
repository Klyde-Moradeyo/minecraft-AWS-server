import os
import datetime
import requests
import time
from .logger import setup_logging

class APIUtil:
    def __init__(self, envs):
        self.logger = setup_logging()  # Setting up logger

        # Ensure that the environment variable exists
        if 'API_URL' not in envs:
            self.logger.error("API_URL not found in environment variables")
            raise ValueError("API_URL not provided")

        self.base_url = envs['API_URL']

    def _get_headers(self):
        """
        Returns the default headers for requests.
        """
        return {'Content-Type': 'application/json'}

    def _construct_url(self, endpoint):
        """
        Constructs a complete URL using the base URL and endpoint.
        """
        return f"{self.base_url}/{endpoint}"

    def _append_metadata(self, data, reason):
        """
        Adds meta data to map
        """
        data["metadata"] = {
                            "requestTime": datetime.datetime.now().isoformat(),
                            "reason": str(reason)
        }
        return data

    def send_to_api(self, data, reason, endpoint="command", timeout=15, retries=3, wait_time=2):
        """
        Sends data to the API and returns the response.
        """
        data = self._append_metadata(data, reason)
        self.logger.info(f"API Payload: {data}")
        url = self._construct_url(endpoint)
        headers = self._get_headers()

        for attempt in range(retries):
            self.logger.info(f"Sending Data to API at endpoint {endpoint} (Attempt: {attempt + 1})")

            try:
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
                response.raise_for_status()

                self.logger.info(f"Received successful response from {endpoint}")
                return response.json()

            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timed out for endpoint: {endpoint}.")
            except requests.exceptions.RequestException as err:
                self.logger.warning(f"Error occurred while sending data to {endpoint}: {err}.")
            
            if attempt < retries - 1:  # To avoid sleeping after the last attempt
                self.logger.info(f"Waiting {wait_time}s before retry.")
                time.sleep(wait_time)

        self.logger.error(f"Failed to send data to API after {retries} attempts.")
        return None
