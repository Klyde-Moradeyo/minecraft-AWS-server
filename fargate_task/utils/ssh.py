import os
import paramiko
import time
from .logger import setup_logging

# Setting up logging
logger = setup_logging()

# Usage examples:
# ssh_util = SSHUtil("machine_ip", "username", "key_path")
# ssh_util.establish_connection()
# ssh_util.run_command("mkdir -p /path/to/directory")
# ssh_util.scp_to_ec2("local_path", "remote_path")

class SSHUtil:
    def __init__(self, machine_ip, username, key_file):
        self.machine_ip = machine_ip
        self.username = username
        self.key_file = key_file

    def _connect(self):
        """
        Establish an SSH connection and return the client.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(self.machine_ip, username=self.username, key_filename=self.key_file)
        except Exception as e:
            logger.error(f"Error connecting to {self.machine_ip}: {str(e)}")
            raise

        return ssh

    def establish_connection(self, retries=5, wait=10):
            """
            Try to establish an SSH connection with retries.
            """
            for _ in range(retries):
                ssh = self._connect()
                if ssh:
                    ssh.close()
                    return True
                time.sleep(wait)
            
            logger.error(f"Unable to establish SSH connection after {retries} attempts.")
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip} after {retries} attempts.")

    def run_command(self, command, capture_output=False):
        """
        SSH into the machine and run the provided command.
        """
        ssh = self._connect()
        if not ssh:
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip}.")
        
        try:
            stdin, stdout, stderr = ssh.exec_command(command)

            # Get Exit status
            exit_status = stdout.channel.recv_exit_status()
            
            # Read and decode output
            err = stderr.read().decode().strip()
            out = stdout.read().decode().strip()

            if exit_status != 0:
                logger.error(f"Command exited with status code {exit_status}.")
                raise Exception(f"Command exited with status code {exit_status}.")
            else:
                logger.info(f"Command '{command}' executed successfully.")
        except Exception as e:
            logger.error(f"Error while executing command '{command}': {e}")
        finally:
            ssh.close()
        
        if capture_output:
            return out


    def scp_to_ec2(self, local_path, remote_path):
        """
        Copy a local file or directory to a remote machine via SCP.
        """
        ssh = self._connect()
        if not ssh:
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip}.")

        scp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        try:
            scp.put(local_path, remote_path)
        except Exception as e:
            logger.error(f"Error copying {local_path} to {remote_path} on {self.machine_ip}: {str(e)}")
            raise e
        scp.close()
        ssh.close()

    def ssh_and_read_file_output(self, file_path):
        """
        SSH into the machine and read the file contents.
        """
        ssh = self._connect()
        if not ssh:
            raise ConnectionError(f"Unable to establish SSH connection to {self.machine_ip}.")
        
        sftp = ssh.open_sftp()
        try:
            with sftp.file(file_path, 'r') as f:
                content = f.read().decode()
            logger.info(f"Read content from {file_path} successfully.")
            return content
        except Exception as e:
            logger.error(f"Error while reading file '{file_path}': {e}")
            raise e
        finally:
            sftp.close()
            ssh.close()