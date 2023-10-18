import os
import tempfile
import yaml
from utils.logger import setup_logging

class FileHelper:
    def __init__(self):
        self.logger = setup_logging() # Setting up logger

    def write_to_file(self, content):
        """
        Write the given content to a temporary file and return its path.
        """
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        return temp_path

    def read_and_delete_file(self, temp_path):
        """
        Read content from a given temporary file and then delete the file.
        """
        if os.path.exists(temp_path):
            with open(temp_path, 'r') as temp:
                content = temp.read()
            os.remove(temp_path)  # Removing the temp file after reading its content
        else:
            content = None
            self.logger.error(f"{temp_path} doesn't exist")
        return content

    def read_from_file(self, file_path):
        """
        Read content from the given file without deleting it.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
        else:
            content = None
            self.logger.error(f"{file_path} doesn't exist")
        return content
    
class YamlHelper:
    def __init__(self, file_path=None, yaml_str=None):
        self.logger = setup_logging()  # Setting up logger
        self.file_path = file_path
        self.yaml_str = yaml_str
        self.variables = {}  # Internal state to keep track of variables
        
        if not self.file_path and not self.yaml_str:
            raise ValueError("Either 'file_path' or 'yaml_str' must be provided!")
        
        if self.file_path:  # Only validate the file if a file path is provided
            self._validate_file()
    
        self.data = self._load_yaml()

    def _validate_file(self):
        """
        Validate the file path and file extension.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Error: '{self.file_path}' does not exist!")
        
        if not self.file_path.endswith('.yml') and not self.file_path.endswith('.yaml'):
            raise ValueError(f"Error: '{self.file_path}' is not a .yml or .yaml file!")

    def _load_yaml(self):
        """
        Load the contents of a YAML from either a file or a string.
        """
        if self.file_path:
            try:
                with open(self.file_path, "r") as file:
                    data = yaml.safe_load(file)
                    return data
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: '{e}'")
                return None
            except Exception as e:
                print(f"Error reading file: '{e}'")
                return None
        elif self.yaml_str:
            try:
                data = yaml.safe_load(self.yaml_str)
                return data
            except yaml.YAMLError as e:
                print(f"Error parsing YAML string: '{e}'")
                return None

    def reload(self):
        """
        Reloads the YAML data from the file.
        """
        self.data = self._load_yaml_file()

    def resolve_placeholders(self, variables={}):
        """
        Recursively replace placeholders in the loaded YAML data with the given variables.
        """
        self.variables.update(variables)
        self.data = self._load_yaml()
        self.data = self._resolve_in_value(self.data, self.variables)
        return self.data
        
    def _resolve_in_value(self, value, variables):
        """
        Recursively replace placeholders in a value (string, list, or dictionary) based on provided variables.
        """
        if isinstance(value, str):
            for key, val in variables.items():
                value = value.replace(f"{{{key}}}", val)
            return value
        elif isinstance(value, list):
            return [self._resolve_in_value(item, variables) for item in value]
        elif isinstance(value, dict):
            return {key: self._resolve_in_value(val, variables) for key, val in value.items()}
        else:
            return value
        
    def get_data(self):
        """
        Returns the loaded data from the YAML file.
        """
        return self.data

    def get_variables(self):
        """
        Returns the loaded data from the YAML file.
        """
        return self.variables