import os
import tempfile
import logging

class FileHelper:
    def __init__(self):
        self.logger = logging.getLogger('FileHelper')

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
