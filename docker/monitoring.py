import time
import json
import os
from datetime import datetime
import requests
from typing import List, Dict, Any
from mcrcon import MCRcon
from mcstatus import JavaServer
from prometheus_client import start_http_server, Gauge

RCON_IP = 'mc-server'
RCON_PORT = os.environ["RCON_PORT"]
RCON_PASS = None # os.environ["RCON_PASS"]
API_GATEWAY_URL = os.environ["API_URL"]
INACTIVE_TIME =  1800  # 30 minutes |  Time in seconds for inactive players check
CHECK_INTERVAL = 60  # Time in seconds for the check interval
LOG_FILE = 'server_monitoring.log'  # Log file name


######################################################################
#                         Helper Functions                           #
######################################################################
def get_env_variables() -> Dict[str, str]:
    env_vars = ["RCON_PORT", "API_URL", "RCON_PASS" , "PROMETHEUS_PORT"]
    return {var: os.getenv(var) for var in env_vars}

######################################################################
#                               LOG                                  #
######################################################################
class LOG:
    def __init__(self, log_file):
        self.log_file = log_file

    def format_data(self, online, players_online, version, time_without_players, timer_status):  
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            "timestamp": timestamp,
            "server_online": online,
            "players_online": players_online,
            "server_version": version,
            "time_without_players": time_without_players,
            "timer_status": timer_status
            }

    def log(self, data):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(data, dict):
            timestamped_data = {'timestamp': timestamp, **data}
            print(timestamped_data)
            self.log_to_file(', '.join([f"{k}: {v}" for k, v in timestamped_data.items()]))
        else:
            print(f"{timestamp}: {data}")
            self.log_to_file(f"{timestamp}: {data}")

    def log_to_file(self, data):
        with open(self.log_file, 'a') as f:
            if isinstance(data, dict):
                f.write(json.dumps(data, indent=4))
            else:
                f.write(data)
            f.write('\n')

######################################################################
#                           Monitor Class                            #
######################################################################
class MonitorError(Exception):
    pass

class MONITOR:
    def __init__(self, server, log, inactive_time, check_interval, api_url, rcon_pass, envs):
        self.server = server
        self.log = log
        self.inactive_time = inactive_time
        self.check_interval = check_interval
        self.api_url = api_url
        self.rcon_pass = rcon_pass
        self.inactive_players_timer_start = None

        # Promtheus Metrics
        self.online_players_gauge = Gauge('minecraft_online_players', 'Number of online players')
        self.server_up_gauge = Gauge('minecraft_server_up', 'Whether the server is up')

        # Start up the server to expose the metrics
        start_http_server(int(envs['PROMETHEUS_PORT']))

    def get_basic_server_info(self):
        try:
            status = self.server.status()
            online = self.server.ping() is not None
            players_online = status.players.online
            version = status.version.name
        except Exception as e:
            online = False
            players_online = 0
            version = None

        return {
            'online': online,
            'players_online': players_online,
            'version': version
        }
    
    def send_to_api(self, command):
        MAX_RETRIES = 3
        TIMEOUT = 5  # seconds

        headers = {'Content-Type': 'application/json'}
        data =  { "action": command }

        log_data = {
            "api_command": command,
            "status": "sending",
            "retries": 0,
            "response_code": None,
            "http_error": None,
            "timeout_error": False,
            "request_error": None,
            "max_retries_exceeded": False
        }
    
        for i in range(MAX_RETRIES):
            try:
                response = requests.post(self.api_url, headers=headers, json=data, timeout=TIMEOUT)
                response.raise_for_status()
                log_data["status"] = "success"
                log_data["response_code"] = response.status_code
                log_data["retries"] = i + 1
                self.log.log(log_data)
                return response
            except requests.exceptions.HTTPError as http_err:
                log_data["status"] = "failure"
                log_data["http_error"] = str(http_err)
            except requests.exceptions.Timeout:
                log_data["status"] = "failure"
                log_data["timeout_error"] = True
            except requests.exceptions.RequestException as req_err:
                log_data["status"] = "failure"
                log_data["request_error"] = str(req_err)

            if i == MAX_RETRIES - 1:
                log_data["max_retries_exceeded"] = True
                log_data["retries"] = i + 1
                self.log.log(log_data)

            wait_time = (2 ** i)  # exponential backoff
            time.sleep(wait_time)

        return None

    def get_inactive_time_string(self):
        minutes, seconds = divmod(self.inactive_time, 60)
        return f"{minutes} minutes {seconds} seconds"

    def run(self):
        while True:
            try:
                basic_info = self.get_basic_server_info()

                server_info = { **basic_info }

                # Update the metrics
                self.online_players_gauge.set(server_info['players_online'])
                self.server_up_gauge.set(server_info['online'])

                if server_info.get('players_online', 0) == 0:
                    if self.inactive_players_timer_start is None:
                        self.inactive_players_timer_start = time.time()
                        data = self.log.format_data(server_info['online'], server_info['players_online'], server_info['version'], 0, "STARTING")
                        self.log.log(data)
                    elif time.time() - self.inactive_players_timer_start >= self.inactive_time: # Send to API Gateway if no players for inactive_time
                        data = self.log.format_data(server_info['online'], server_info['players_online'], server_info['version'], self.get_inactive_time_string(), "EXPIRED - SIGNALING MC SERVER STOP")
                        self.log.log(data)
                        self.send_to_api("stop")
                        self.inactive_players_timer_start = None
                    else:
                        elapsed_time = int(time.time() - self.inactive_players_timer_start)
                        data = self.log.format_data(server_info['online'], server_info['players_online'], server_info['version'], elapsed_time, "RUNNING")
                        self.log.log(data)
                else:
                    self.inactive_players_timer_start = None
                    data = self.log.format_data(server_info['online'], server_info['players_online'], server_info['version'], 0, "RESET")
                    self.log.log(data)

            except MonitorError:
                self.log.log("Monitoring error occurred")

            # Wait for the check interval before checking again
            time.sleep(self.check_interval)

if __name__ == "__main__":
    envs = get_env_variables()
    RCON_IP = 'mc-server'
    RCON_PORT = envs["RCON_PORT"]
    RCON_PASS = envs["RCON_PASS"]
    API_GATEWAY_URL = envs["API_URL"] + "/command"
    INACTIVE_TIME =  1800  # 30 minutes
    CHECK_INTERVAL = 60  # Time in seconds for the check interval
    LOG_FILE = 'server_monitoring.log'  # Log file name

    minecraft_server = JavaServer.lookup(f"{RCON_IP}:{RCON_PORT}")
    log = LOG(LOG_FILE)
    monitor = MONITOR(minecraft_server, log, INACTIVE_TIME, CHECK_INTERVAL, API_GATEWAY_URL, RCON_PASS, envs)
    monitor.run()