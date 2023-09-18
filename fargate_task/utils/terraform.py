import subprocess
import os
from .logger import setup_logging

logger = setup_logging()

class TerraformError(Exception):
    pass

class TerraformHelper:

    def __init__(self, path: str):
        """
        Constructor for the TerraformHelper class.

        Parameters:
            path (str): The working directory for Terraform commands.
        """
        self._validate_directory(path)
        self._check_terraform_installed()
        
        self.path = path

        # Run Terraform init during initialization
        self.run_command("init")

    def _validate_directory(self, path: str):
        """
        Validates if the directory exists and is a directory.
        """
        if not os.path.exists(path):
            raise ValueError(f"Directory {path} does not exist.")
        if not os.path.isdir(path):
            raise ValueError(f"{path} is not a directory.")

    def _check_terraform_installed(self):
        """
        Checks if Terraform is installed.
        """
        try:
            subprocess.run(["terraform", "-v"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise TerraformError("Terraform command failed.")
        except FileNotFoundError:
            raise TerraformError("Terraform is not installed or not in PATH.")
    

    def run_command(self, *args):
        """
        Executes a Terraform command with the given arguments.

        Parameters:
            *args: The Terraform command and its arguments.
        
        Returns:
            str: The output of the command.
        """
        # Prepare the command
        terraform_command = ["terraform"] + list(args)
        if args[0] in ["apply", "destroy"]:
            terraform_command.append("--auto-approve")

        # Run the terraform command
        try:
            if args[0] == "output":
                output = subprocess.run(terraform_command, cwd=self.path, check=True, capture_output=True, text=True)
                result = output.stdout.strip().strip('"')
                return result
            else:
                result = subprocess.run(terraform_command, cwd=self.path, check=True, capture_output=False, text=True)
                return result.stdout
        except subprocess.CalledProcessError as e:
            raise TerraformError(f"Error running terraform {args}: {e.stderr}")
