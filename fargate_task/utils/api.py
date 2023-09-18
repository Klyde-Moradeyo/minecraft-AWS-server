import requests
from logger import setup_logging

# Setting up logging
logger = setup_logging()

def send_to_api(data, url):
    """
    Send Data to API Gateway
    """
    if url is None:
        print("API_URL is not set in the environment variables")
        return None

    url += "/command"
    
    headers = {'Content-Type': 'application/json'}
    
    logger.info(f"Sending Data to API: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Response from API: {response}")
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logger.error(f"Error occurred: {err}")
        return None

    return response

