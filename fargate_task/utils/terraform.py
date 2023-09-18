import subprocess
import os
from logger import setup_logging

logger = setup_logging()

# example usage
# # import the required classes and exceptions
# from utils.terraform import TerraformHelper, TerraformError

# # instantiate the helper with the directory where your Terraform configurations reside
# terraform = TerraformHelper("/path/to/your/terraform/configuration")

# # Examples of using run_command:

# # To initialize the Terraform configuration
# try:
#     output = terraform.run_command("init")
#     print(output)
# except TerraformError as e:
#     print(f"Error: {e}")

# # To apply the Terraform configuration
# try:
#     output = terraform.run_command("apply")
#     print(output)
# except TerraformError as e:
#     print(f"Error: {e}")

# # To get output values from the Terraform configuration
# try:
#     output_value = terraform.run_command("output", "some_output_variable_name")
#     print(f"The output value is: {output_value}")
# except TerraformError as e:
#     print(f"Error: {e}")

# # ... and similarly for other Terraform commands.


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
