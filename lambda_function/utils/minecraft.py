from mcstatus import JavaServer
from typing import Dict, Any
from .logger import setup_logging

class MinecraftServerChecker:
    def __init__(self, ip: str, port: str):
        self.logger = setup_logging()
        self.server_address = f"{ip}:{port}"
        self.java_server = JavaServer.lookup(self.server_address)

    def check(self) -> Dict[str, Any]:
        """
        Checks the status of the Minecraft server.
        """
        try:
            status = self.java_server.status()
            return {
                'online': self.java_server.ping() is not None,
                'players_online': status.players.online,
                'version': status.version.name
            }
        except Exception as e:
            self.logger.warning(f"Warning: Could not check the Minecraft server. Maybe its offline? Error:\n'{str(e)}'.")
            return {
                'online': False,
                'players_online': 0,
                'version': 'unknown'
            }
