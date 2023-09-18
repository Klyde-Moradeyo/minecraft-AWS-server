# config/__init__.py

import os
from utils.aws import *
from utils.git import GitUtil
from utils.file_operations import write_to_tmp_file
from utils.terraform import TerraformHelper, TerraformError

# --- AWS ---
AWS_REGION = get_region()

# --- AWS SSM ---
SSM_FARGATE_COMMAND_NAME = os.getenv('BOT_COMMAND_NAME')
SSM_GIT_PRIVATE_KEY_NAME = os.getenv('GIT_PRIVATE_KEY')
SSM_EC2_PRIVATE_KEY_NAME = os.getenv('EC2_PRIVATE_KEY')

# --- Git ---
GIT_REPO_NAME = "tf_manifests"
GIT_REPO_URL = "git@github.com:Klyde-Moradeyo/minecraft-AWS-server.git"
GIT_BRANCH = GitUtil.get_git_branch()
SSH_KEY_STR = get_ssm_param(SSM_EC2_PRIVATE_KEY_NAME)
GIT_REPO_CONFIG =   { 
                        "name": GIT_REPO_NAME,
                        "url": GIT_REPO_URL, 
                        "branch": GIT_BRANCH,
                        "paths": {
                            "git_ssh_key": write_to_tmp_file(SSH_KEY_STR),
                            "tf_mc_infra_manifests": os.path.join(GIT_REPO_NAME, "terraform", os.environ['ENVIRONMENT'], "minecraft_infrastructure"),
                            "tf_mc_infra_handler": os.path.join(GIT_REPO_NAME, "terraform", os.environ['ENVIRONMENT'], "infrastructure_handler"),
                            "tf_mc_infra_scripts": os.path.join(GIT_REPO_NAME, "scripts")
                        }
                    }

# --- Terraform ---
os.environ['TF_TOKEN_app_terraform_io'] = get_ssm_param(os.environ['TF_USER_TOKEN']) # Terraform Cloud Token

# --- EC2 Login Details ---
EC2_USERNAME = 'ubuntu'
EC2_PRIVATE_KEY = get_ssm_param(SSM_EC2_PRIVATE_KEY_NAME)
EC2_PRIVATE_KEY_PATH = write_to_tmp_file(EC2_PRIVATE_KEY)
os.chmod(EC2_PRIVATE_KEY_PATH, 0o600)

# --- Container's Job ---
JOB = get_ssm_param(SSM_FARGATE_COMMAND_NAME)
