import time
import json
import os
from datetime import datetime
from mcrcon import MCRcon
from mcstatus import JavaServer
import requests

# These are placeholders, replace with your actual details
RCON_IP = 'mc-server'
RCON_PORT = os.environ["RCON_PORT"]
RCON_PASS = None # os.environ["RCON_PASS"]
API_GATEWAY_URL = os.environ["API_URL"]
INACTIVE_TIME =  1800  # 30 minutes |  Time in seconds for inactive players check
CHECK_INTERVAL = 60  # Time in seconds for the check interval
LOG_FILE = 'server_monitoring.log'  # Log file name

minecraft_server = JavaServer.lookup(f"{RCON_IP}:{RCON_PORT}")

def send_to_api(data):
    # API Gateway URL
    url = os.getenv('API_URL')
    if url is None:
        log_to_console_and_file("API_URL is not set in the environment variables")
        return None

    url += "/minecraft-prod/command"
    
    headers = {'Content-Type': 'application/json'}
    
    log_to_console_and_file(f"Sending Data to API: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        log_to_console_and_file(f"Error occurred: {err}")
        raise

    log_to_console_and_file(f"Data: {data} \nResponse: \n{response.json()}")  # To print the response from server
    
    return response

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_basic_server_info():
    try:
        status = minecraft_server.status()
        return {
            'online': minecraft_server.ping() is not None,
            'players_online': status.players.online,
            'version': status.version.name
        }
    except Exception:
        return {
            'online': False,
            'players_online': 0,
            'version': 'unknown'
        }

def get_detailed_server_info():
    with MCRcon(RCON_IP, RCON_PASS, port=RCON_PORT) as mcr:
        tps = mcr.command("/tps")
        uptime = mcr.command("/uptime")  # You might need a plugin or mod for this
        debug = mcr.command("/debug")
        latency = mcr.command("/ping")  # You might need a plugin or mod for this

    return {
        'tps': tps,
        'uptime': uptime,
        'debug': debug,
        'latency': latency
    }

def log_to_file(data):
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(data, indent=4))
        f.write('\n')

def log_to_console_and_file(data):
    timestamped_data = {**data, 'timestamp': get_timestamp()}
    print(timestamped_data)
    log_to_file(timestamped_data)

if __name__ == "__main__":
    inactive_players_timer_start = None

    while True:
        try:
            basic_info = get_basic_server_info()
            # detailed_info = get_detailed_server_info() if basic_info['online'] else {}

            # server_info = {**basic_info, **detailed_info}
            server_info = {**basic_info}

            # Log the server info
            log_to_console_and_file(server_info)

            if server_info.get('players_online', 0) == 0:
                if inactive_players_timer_start is None:
                    inactive_players_timer_start = time.time()
                elif time.time() - inactive_players_timer_start >= INACTIVE_TIME:
                    # Send to API Gateway if no players for INACTIVE_TIME
                    data = { "command": "stop" }
                    send_to_api(data)
                    inactive_players_timer_start = None
            else:
                inactive_players_timer_start = None

        except Exception as e:
            log_to_console_and_file({'Error': e})

        # Wait for the check interval before checking again
        time.sleep(CHECK_INTERVAL)
