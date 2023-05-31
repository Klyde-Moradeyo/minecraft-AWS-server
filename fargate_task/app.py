import boto3
import os
import shutil
import tempfile
import requests
import json
import logging
import subprocess
import sys
import stat
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from git import Repo, Actor
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Enable detailed boto3 logging
logging.basicConfig(level=logging.DEBUG)

######################################################################
#                   General Functions                                #
######################################################################
# Fetch the SSH key from the Parameter Store
def get_ssm_param(param_name):
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    param = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
    contents = param["Parameter"]["Value"]
        
    return contents

def put_ssm_param(param_name, param_value):
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    ssm_client.put_parameter(
        Name=param_name,
        Value=param_value,
        Type='SecureString',
        Overwrite=True
    )

def write_to_tmp_file(content):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file.flush() # Ensure any buffered data is written to the file
        dir = temp_file.name
    return dir

def create_ec2_key_pair(key_name):
    # Generate an RSA key pair
    # - public_exponent: The public exponent (e) is a value used in the RSA algorithm, usually set to 65537
    # - key_size: The size of the key in bits, here set to 2048 bits
    # - backend: The backend used for cryptographic operations, here we use the default_backend
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialize the private key in PEM format (Privacy-Enhanced Mail, a widely used format for storing and sending cryptographic keys)
    # - encoding: The format used to encode the key, here PEM
    # - format: The format used for the private key, here PKCS8 (Public-Key Cryptography Standards #8)
    # - encryption_algorithm: The algorithm used to encrypt the key, here no encryption is used
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Get the public key and serialize it in OpenSSH format
    public_key = private_key.public_key()
    public_key_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    private_key_str = private_key_pem.decode('utf-8')
    public_key_str = public_key_ssh.decode('utf-8')

    # Create a new key pair on AWS
    ec2_client = boto3.client('ec2', region_name='eu-west-2')

    try:
        # Delete the existing key pair
        ec2_client.delete_key_pair(KeyName=key_name)
    except:
        pass  # If the key pair doesn't exist, ignore the error

    # Create a new key pair
    response = ec2_client.import_key_pair(KeyName=key_name, PublicKeyMaterial=public_key_str)

    return private_key_str

def get_command():
    ssm_client = boto3.client('ssm', region_name='eu-west-2')
    response = ssm_client.get_parameter(
        Name='/mc_server/BOT_COMMAND',
        WithDecryption=True
    )
    return response['Parameter']['Value']

def run_bash_script(script_path, log_file_path, *script_args):
    try:
        # Ensure the bash script file has execute permissions
        st = os.stat(script_path)  # Get the current permissions of the file
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)  # Add execute permission for the owner

        # Note: It's generally safer to pass the arguments in as a list,
        # especially if they might be user-provided, to avoid shell injection attacks.
        process = subprocess.Popen(
            [script_path] + list(script_args), 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        # Open the log file
        with open(log_file_path, 'w') as log_file:
            if stdout:
                log_file.write(stdout.decode())
            if stderr:
                log_file.write(stderr.decode())

        if process.returncode != 0:
            stderr = stderr.decode()
            logging.error(f"Script {script_path} failed with error: {stderr}")
            sys.exit(1)
        
    except Exception as e:
        logging.error(f"Failed to execute script {script_path}: {str(e)}")
        sys.exit(1)

################################
#            SSH               #
################################   
def add_host_key(hostname):
    try:
        # Run the ssh-keyscan command
        result = subprocess.run(['ssh-keyscan', hostname], capture_output=True, text=True, check=True)

        # Write the output to the known_hosts file
        with open(os.path.expanduser('~/.ssh/known_hosts'), 'a') as file:
            file.write(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"ssh-keyscan failed: {e.stderr}")

def create_ssh_client(ip, username, key_file):
    add_host_key(ip) # add host ip
    ssh = SSHClient() # Create an SSH client
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())  # WarningPolicy

    # Connect to the server
    try:
        ssh.connect(ip, username=username, key_filename=key_file)
    except Exception as e:
        logging.error(f"Failed to connect to {ip}: {str(e)}")
        sys.exit(1)

    return ssh

def scp_to_ec2(ip, username, key_file, local_path, remote_path):
    ssh = create_ssh_client(ip, username, key_file)
    if ssh is None:
        return
    
    # Ensure the remote directory exists
    remote_dir = os.path.dirname(remote_path)
    stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {remote_dir}')
    stdout.channel.recv_exit_status()  # Wait for the command to finish

    try:
        # SCPCLient takes a paramiko transport as its argument
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_path, remote_path)  # Copy from local to remote
    except Exception as e:
        logging.error(f"Failed to copy file to {ip}: {str(e)}")
        sys.exit(1)
    
    ssh.close()

def ssh_and_run_script(ip, username, key_file, script_path, log_file_path):
    ssh = create_ssh_client(ip, username, key_file)
    if ssh is None:
        return

    try:
        # Run the bash script and redirect its output to a log file
        stdin, stdout, stderr = ssh.exec_command(f"bash {script_path} > {log_file_path}")
        
        # Log the output of the script
        logging.info(stdout.read().decode())
        logging.error(stderr.read().decode())
    except Exception as e:
        logging.error(f"Failed to execute script on {ip}: {str(e)}")
        sys.exit(1)

    ssh.close()

################################
#         Git Functions        #
################################
def git_clone(repo_url, dir, branch, ssh_key):
    # Set the SSH key environment variable and disable host key checking
    custom_ssh_env = os.environ.copy()
    custom_ssh_env["GIT_SSH_COMMAND"] = f"ssh -v -i {ssh_key} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    
    try:
        repo = Repo.clone_from(repo_url, dir, branch=branch, env=custom_ssh_env)
    except Exception as e:
        raise Exception(f"Git clone failed:\n{str(e)}")
    
    return repo

def git_commit(repo, commit_message, author_name, author_email):
    author = Actor(author_name, author_email)
    repo.git.add(update=True)  # Stage all changes
    repo.index.commit(commit_message, author=author)

def git_push(repo, ssh_key, remote_name="origin", branch="main"):
    # Set the SSH key environment variable and disable host key checking
    custom_ssh_env = os.environ.copy()
    custom_ssh_env["GIT_SSH_COMMAND"] = f"ssh -v -i {ssh_key} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    
    remote = repo.remote(remote_name)

    try:
        with repo.git.custom_environment(GIT_SSH_COMMAND=custom_ssh_env["GIT_SSH_COMMAND"]):
            remote.push(branch)
    except Exception as e:
        raise Exception(f"Git push failed:\n{str(e)}")
    
################################
#     Terraform Functions      #
################################
class TerraformError(Exception):
    pass

def run_terraform_command(directory, command):
    # Check if directory exists
    if not os.path.exists(directory):
        raise ValueError(f"Directory {directory} does not exist.")
    if not os.path.isdir(directory):
        raise ValueError(f"{directory} is not a directory.")
    
    # Check Terraform is installed
    try:
        subprocess.run(["terraform", "-v"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        raise TerraformError("Terraform is not installed or not in PATH.")
    
    # Prepare the command
    terraform_command = ["terraform", command]
    if command in ["apply", "destroy"]:
        terraform_command.append("-auto-approve")

    # Run the terraform command
    try:
        result = subprocess.run(terraform_command, cwd=directory, check=True, capture_output=False, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise TerraformError(f"Error running terraform {command}: {e.stderr}")

######################################################################
#                       Server Handler                               #
######################################################################
def server_handler(command):
    ssh_key = get_ssm_param("dark-mango-bot-private-key") # SSH Key name from system manager parameter store
    tf_api_key = get_ssm_param("terraform-cloud-user-api") # terraform cloud api keyget_ssm_param(ssh_key_name))

    # Repo containing terraform manifests and scripts
    repo_name = "tf_manifests"
    tf_manifest_repo = { 
        "name": repo_name,
        "url": "git@github.com:Klyde-Moradeyo/minecraft-AWS-server.git", 
        "branch": "main",
        "ssh_key": f"{write_to_tmp_file(ssh_key)}",
        "paths": {
            "tf_mc_infra_manifests": os.path.join(repo_name, "terraform", "minecraft_infrastructure"),
            "tf_private_key_folder": os.path.join(repo_name, "terraform", "minecraft_infrastructure", "private-key"),
            "tf_mc_infra_scripts": os.path.join(repo_name, "scripts")
        }
    }
    
    # Git Clone and copy files to minecraft_infra directory
    git_clone(tf_manifest_repo["url"], repo_name, tf_manifest_repo["branch"], tf_manifest_repo["ssh_key"])
    shutil.copytree(tf_manifest_repo["paths"]["tf_mc_infra_scripts"], os.path.join(tf_manifest_repo["paths"]["tf_mc_infra_manifests"], "scripts")) # Copy tf_mc_infra_scripts folder to tf_mc_infra_manifests folder
    
    os.environ['TF_TOKEN_app_terraform_io'] = tf_api_key

    # run_bash_script(os.path.join(tf_manifest_repo["paths"]["tf_mc_infra_scripts"], "ec2_install.sh"), "./install.log")
    # run_bash_script(os.path.join(tf_manifest_repo["paths"]["tf_mc_infra_scripts"], "prepare_ec2_env.sh"), "./prepare_env.log")
    # run_bash_script(os.path.join(tf_manifest_repo["paths"]["tf_mc_infra_scripts"], "post_mc_server_shutdown.sh."), "./server_shutdown.log")

    if command == "start":
        private_key = create_ec2_key_pair("terraform-key")
        put_ssm_param("/mc_server/private_key", private_key)
        run_terraform_command(tf_manifest_repo["paths"]["tf_mc_infra_manifests"], "init")
        run_terraform_command(tf_manifest_repo["paths"]["tf_mc_infra_manifests"], "apply")

    elif command == "stop":
        run_terraform_command(tf_manifest_repo["paths"]["tf_mc_infra_manifests"], "init")
        run_terraform_command(tf_manifest_repo["paths"]["tf_mc_infra_manifests"], "destroy")
    else:
        print("error command not found")
    
    print("Server Handler Completed Successfully")
        
if __name__ == "__main__":
    job = get_command()
    server_handler(job)
