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
                state_data = json.load(f)
            
            # Try to convert keys to integers - In json keys are stored as strings which causes issues with json
            int_keys_state = {}
            for key, value in state_data.items():
                try:
                    int_key = int(key)  # Convert key to int
                    int_keys_state[int_key] = value
                except ValueError:
                    int_keys_state[key] = value  # Keep original key if not convertible

            return int_keys_state
        except json.JSONDecodeError as e:
            self.logger.error(f"state - '{self.file_name}' - Failed to decode: {e}")
        except Exception as e:
            self.logger.error(f"state - '{self.file_name}' - Failed to load: {e}")

        return {}  # if there's an error loading the state Return an empty state 
    
    def has_data(self):
        """
        Check if the state has any data.
        """
        return bool(self.state)

    def save_state(self, value):
        self.state = value
        self._write_state()

    def get_state(self):
        self.logger.info(f"state - '{self.file_name}' - Getting State | state {self.state}")
        return self.state

    def _write_state(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.state, f, indent=4)
            self.logger.info(f"state - '{self.file_name}' - Saving State")
        except Exception as e:
            self.logger.error(f"Failed to write '{self.file_name}': {e}")
