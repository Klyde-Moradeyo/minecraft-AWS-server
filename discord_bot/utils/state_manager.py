import json
import os
from utils.logger import setup_logging

class StateManager:
    def __init__(self, file_path):
        self.logger = setup_logging()
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.state = self._load_initial_state()

    def _ensure_directory_exists(self):
        dir_path = os.path.dirname(self.file_path)
        os.makedirs(dir_path, exist_ok=True)

    def _load_initial_state(self):
        self._ensure_directory_exists()

        if not os.path.exists(self.file_path):
            self.logger.warn(f"state - '{self.file_path}' - File Not Found")
            return {}  # Start with an None state if no file exists

        try:
            self.logger.info(f"state - '{self.file_path}' - Initial State Loaded")
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"state - '{self.file_name}' - Failed to decode: {e}")
        except Exception as e:
            self.logger.error(f"state - '{self.file_name}' - Failed to load: {e}")

        return {}  # if there's an error loading the state Return an empty state 
    
    def isStateExist(self):
        if self.state:
            return True
        else:
            return False

    def save_state(self, value):
        self.state = value
        self._write_state()
        self.logger.info(f"state - '{self.file_name}' - Updating State")

    def load_state(self):
        self.logger.info(f"state - '{self.file_name}' - Loading State")
        return self.state

    def _write_state(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to write '{self.file_name}': {e}")
