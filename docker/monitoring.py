import time
import json
from datetime import datetime
from mcrcon import MCRcon
from mcstatus import JavaServer
import requests

# These are placeholders, replace with your actual details
RCON_IP = 'mc-server'
RCON_PORT = 25565
RCON_PASS = 'your_rcon_password'
API_GATEWAY_URL = 'https://your-api-gateway.url'
INACTIVE_TIME = 60  # 3600  # Time in seconds for inactive players check
CHECK_INTERVAL = 5  # Time in seconds for the check interval
LOG_FILE = 'monitoring.log'  # Log file name

minecraft_server = JavaServer.lookup(f"{RCON_IP}:{RCON_PORT}")

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

def send_to_api_gateway(data):
    response = requests.post(API_GATEWAY_URL, json=data)
    return response.status_code

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

            if server_info.get('players_online', 0) > 0:
                inactive_players_timer_start = time.time()
            elif inactive_players_timer_start and time.time() - inactive_players_timer_start >= INACTIVE_TIME:
                # Send to API Gateway if no players for INACTIVE_TIME
                print("sending to gateway")
                send_to_api_gateway(server_info)
                inactive_players_timer_start = None

        except Exception as e:
            error_message = f"Connection Unsuccessful: Server is offline or unreachable: {e}"
            log_to_console_and_file({'Error': error_message})

        # Wait for the check interval before checking again
        time.sleep(CHECK_INTERVAL)
