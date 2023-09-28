from mcstatus import JavaServer
from typing import Dict, Any
from .logger import setup_logging

# Setting up logging
logger = setup_logging()

def check_mc_server(ip: str, port: str) -> Dict[str, Any]:
    try:
        minecraft_server = JavaServer.lookup(f"{ip}:{port}")

        status = minecraft_server.status()
        return {
            'online': minecraft_server.ping() is not None,
            'players_online': status.players.online,
            'version': status.version.name
        }
    except Exception:
        logger.warning("Warning: Could not check the Minecraft server. Maybe its offline?")
        return {
            'online': False,
            'players_online': 0,
            'version': 'unknown'
        }