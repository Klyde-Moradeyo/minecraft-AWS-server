import boto3
import os
import shutil
import tempfile
import requests
import json
import logging
from python_terraform import Terraform
from git import Repo, Actor

logger = logging.getLogger()
logger.setLevel(logging.INFO)


######################################################################
#                           Functions                                #
######################################################################
# Fetch the SSH key from the Parameter Store
def get_git_ssh_key(param_name):
    ssm_client = boto3.client("ssm")

    param = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
    ssh_key = param["Parameter"]["Value"]

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as ssh_key_file:
        ssh_key_file.write(ssh_key.strip())
        ssh_key_file.flush() # Ensure any buffered data is written to the file
        ssh_key_dir = ssh_key_file.name
        
    return ssh_key_dir


################################
#         Git Functions        #
################################
def git_clone(repo_url, dir, branch, ssh_key):
    # Set the SSH key environment variable and disable host key checking
    custom_ssh_env = os.environ.copy()
    custom_ssh_env["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    
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
    custom_ssh_env["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    
    remote = repo.remote(remote_name)

    try:
        with repo.git.custom_environment(GIT_SSH_COMMAND=custom_ssh_env["GIT_SSH_COMMAND"]):
            remote.push(branch)
    except Exception as e:
        raise Exception(f"Git push failed:\n{str(e)}")
    
################################
#     Terraform Functions      #
################################
def terraform_init(tf_obj):
    return_code, stdout, stderr = tf_obj.init(capture_output=True)

    if return_code != 0:
        raise Exception(f"Terraform init failed:\n{stderr}")

    return stdout

def terraform_apply(tf_obj):
    return_code, stdout, stderr = tf_obj.apply(skip_plan=True, capture_output=True, auto_approve=True)

    if return_code != 0:
        raise Exception(f"Terraform apply failed:\n{stderr}")

    return stdout

def terraform_destroy(tf_obj):
    return_code, stdout, stderr = tf_obj.destroy(capture_output=True, auto_approve=True)

    if return_code != 0:
        raise Exception(f"Terraform destroy failed:\n{stderr}")

    return stdout

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    # SSH Key name from system manager parameter store
    ssh_key_name = "dark-mango-bot-private-key" 

    # Repo containing terraform manifests and scripts
    tf_manifest_repo = { 
                        "url": "https://github.com/Klyde-Moradeyo/minecraft-AWS-server.git", 
                        "branch": "main",
                        "ssh_key": f"{get_git_ssh_key(ssh_key_name)}"
                        }
    
    # Repo contains tf_state files
    # Warn: This is not best practice but due to cost and time it is better to store it here
    # Enhancement: Tf_state files Should be stored in personal onedrive
    miscellaneous_repo = { 
                        "url": "https://github.com/Klyde-Moradeyo/miscellaneous.git", 
                        "branch": "main",
                        "ssh_key": f"{get_git_ssh_key(ssh_key_name)}"
                        }

    print(f"repo: {tf_manifest_repo}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        git_clone(tf_manifest_repo["url"], temp_dir, tf_manifest_repo["branch"], tf_manifest_repo["ssh_key"])
        # os.remove(repo["ssh_key"]) # Remove the SSH key file

        # Directories
        scripts_folder = os.path.join(temp_dir, "scripts")
        eip_txt_file = os.path.join(temp_dir, "terraform", "eip-lambda", "EIP.txt")

        # Minecraft Infrasture Directories
        tf_private_key_folder = os.path.join(temp_dir, "terraform", "minecraft_infrastructure", "private-key")
        tf_mc_infra_manifests = os.path.join(temp_dir, "terraform", "minecraft_infrastructure")
        tf_mc_infra_scripts = os.path.join(tf_mc_infra_manifests, "scripts")

        ## Copy Files needed for tf_apply
        shutil.copytree(scripts_folder, tf_mc_infra_scripts, dirs_exist_ok=True)
        shutil.copy2(eip_txt_file, tf_mc_infra_manifests)
    
        # Create Ec2 Instance private Key=
        # create_private_key("terraform_key.pem", tf_private_key_folder)

        # Create a Terraform object in minecraft_infrastrucutre dir 
        tf = Terraform(working_dir=tf_mc_infra_manifests)
        terraform_init(tf)
        # terraform_apply(tf)
    
    return {
        'statusCode': 200,
        'body': json.dumps("Success")
    }
        
# lambda_handler("event", "context")

# logger.info('This is an INFO level message.')
#     logger.error('This is an ERROR level message.')
