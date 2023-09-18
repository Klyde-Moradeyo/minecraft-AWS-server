import os
import paramiko
import time
from logger import setup_logging

# Setting up logging
logger = setup_logging()

# # Importing the necessary classes and functions
# from your_module import SSHUtil

# # Initialize the SSHUtil object with required parameters.
# ssh_util = SSHUtil(machine_ip="machine_ip_here", username="your_username", key_file="path_to_key_file")

# # Running a command on the remote machine.
# output = ssh_util.run_command("ls -la", capture_output=True)
# print("Output of the command:\n", output)

# # Copying a file to the remote machine.
# local_file_path = "/path/to/local/file.txt"
# remote_file_path = "/path/on/remote/machine/file.txt"
# ssh_util.scp_to_ec2(local_file_path, remote_file_path)

# # Reading the content of a file from the remote machine.
# file_content = ssh_util.ssh_and_read_file_output(remote_file_path)
# print("Content of the remote file:\n", file_content)

# # The connection will be closed automatically when the ssh_util object is garbage collected. 
# # If you want to close it explicitly, you can delete the object:
# # del ssh_util


class SSHUtil:
    def __init__(self, machine_ip, username, key_file, retries=5, wait=10):
        self.machine_ip = machine_ip
        self.username = username
        self.key_file = key_file
        self.retries = retries
        self.wait = wait
        self.ssh = self._connect()
        
    def _connect(self):
        """
        Establish an SSH connection and return the client with retries.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        for _ in range(self.retries):
            try:
                ssh.connect(self.machine_ip, username=self.username, key_filename=self.key_file)
                return ssh
            except Exception as e:
                logger.error(f"Error connecting to {self.machine_ip} on attempt {_ + 1}: {str(e)}")
                if _ < self.retries - 1:  # if not on the last attempt
                    time.sleep(self.wait)
                else:
                    raise


    def __del__(self):
        if self.ssh:
            self.ssh.close()

    def run_command(self, command, capture_output=False):
        """
        SSH into the machine and run the provided command.
        """
        if not self.ssh:
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip}.")
        
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)

            # Get Exit status
            exit_status = stdout.channel.recv_exit_status()
            
            # Read and decode output
            err = stderr.read().decode().strip()
            out = stdout.read().decode().strip()

            if exit_status != 0:
                logger.error(f"Command exited with status code {exit_status}.")
                raise Exception(f"Command exited with status code {exit_status}. Error: {err}")
            else:
                logger.info(f"Command '{command}' executed successfully.")
        except Exception as e:
            logger.error(f"Error while executing command '{command}': {e}")
            raise
        
        if capture_output:
            return out
        
    def run_script(self, script_path, log_file_path, *args):
        if not self.ssh:
            logger.error(f"SSH connection could not be established to {self.machine_ip}.")
            raise Exception(f"SSH connection could not be established to {self.machine_ip}.")

        # Convert args to a string
        args_str = ' '.join(args)

        try: 
            # Run the bash script and redirect its output to a log file
            stdin, stdout, stderr = self.ssh.exec_command(f"sudo bash {script_path} {args_str} > {log_file_path} 2>&1")
            
            # Wait for the command to finish
            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                script_logs = self.ssh_and_read_file_output(log_file_path)
                logger.error(f"{script_logs} \nScript exited with status code {exit_status}.")
                raise Exception(f"Script exited with status code {exit_status}.")
        except Exception as e:
            logger.error(f"Failed to execute script on {self.machine_ip}: {str(e)}.")
            raise

    def scp_to_machine(self, local_path, remote_path):
        """
        Copy a local file or directory to a remote machine via SCP.
        """
        if not self.ssh:
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip}.")

        with paramiko.SFTPClient.from_transport(self.ssh.get_transport()) as scp:
            try:
                scp.put(local_path, remote_path)
            except Exception as e:
                logger.error(f"Error copying {local_path} to {remote_path} on {self.machine_ip}: {str(e)}")
                raise

    def read_file_output(self, file_path):
        """
        SSH into the machine and read the file contents.
        """
        if not self.ssh:
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip}.")
        
        with self.ssh.open_sftp() as sftp:
            try:
                with sftp.file(file_path, 'r') as f:
                    content = f.read().decode()
                logger.info(f"Read content from {file_path} successfully.")
                return content
            except Exception as e:
                logger.error(f"Error while reading file '{file_path}': {e}")
                raise