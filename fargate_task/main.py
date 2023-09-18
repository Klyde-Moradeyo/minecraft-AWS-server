import shutil
from config import *
from utils.logger import setup_logging
from utils.ssh import SSHUtil
from utils.file_operations import *
from utils.script_runner import *

# Setting up logging
logger = setup_logging()

class ServerManager:

    def __init__(self):
        self.configured = self.check_configuration()

    def check_configuration(self):
        # Check for required configurations
        required_configs = [
            # AWS
            AWS_REGION, 
            
            # SSM
            SSM_FARGATE_COMMAND_NAME, SSM_GIT_PRIVATE_KEY_NAME, SSM_EC2_PRIVATE_KEY_NAME,

            # EC2
            EC2_USERNAME, EC2_PRIVATE_KEY, EC2_PRIVATE_KEY_PATH,

            # Git
            GIT_REPO_NAME, GIT_REPO_URL, GIT_BRANCH, SSH_KEY_STR, GIT_REPO_CONFIG,

            # Terraform Cloud
            os.environ.get('TF_TOKEN_app_terraform_io'),
            
            # Job
            JOB
        ]

        for config in required_configs:
            if not config:
                logger.error(f"Configuration for {config} is missing!")
                return False
        logger.info("All configurations are set!")
        return True
    
    def server_handler(self, command):
        # Initilize Git Util and Clone tf_manfiests repo
        GIT_UTIL = GitUtil(GIT_REPO_CONFIG["paths"]["git_ssh_key"])
        GIT_UTIL.clone(GIT_REPO_CONFIG["url"], GIT_REPO_CONFIG["name"], GIT_REPO_CONFIG["branch"])

        # Copy scripts folder to tf_mc_infra_manifests folder
        shutil.copytree(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_manifests"], "scripts"))

        # Configure Infrastructure Handler
        TF_INFRA_HANDLER = TerraformHelper(GIT_REPO_CONFIG["paths"]["tf_mc_infra_handler"])

        # Get Infrastructure Handler Outputs
        API_URL = TF_INFRA_HANDLER.run_command("output", "api_gateway_url")
        MACHINE_IP = TF_INFRA_HANDLER.run_command("output", "eip")
        S3_URI = TF_INFRA_HANDLER.run_command("output", "mc_s3_bucket_uri")
        MC_PORT = TF_INFRA_HANDLER.run_command("output", "mc_port")
        
        if command == "start":       
            # Install Script Paths
            local_install_script_path = os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], "ec2_install.sh")
            remote_install_script_path = "setup/scripts/ec2_install.sh"
            remote_install_logs_path = "setup/logs/install.log"

            # Prepare Env Script Paths
            local_prepare_script_path = os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], "prepare_ec2_env.sh")
            remote_prepare_script_path = "setup/scripts/prepare_ec2_env.sh"
            remote_prepare_logs_path = "setup/logs/prepare.log"

            rcon_pass = None

            # Helper Function Script paths
            local_helper_script_path = os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], "helper_functions.sh")
            remote_helper_script_path = "setup/scripts/helper_functions.sh"

            # Configure Minecraft Infrastructure
            TF_MINECRAFT_INFRA = TerraformHelper(GIT_REPO_CONFIG["paths"]["tf_mc_infra"])
            TF_MINECRAFT_INFRA.run_command("apply")

            # Initilize SSH Util
            SSH_UTIL = SSHUtil(MACHINE_IP, EC2_USERNAME, EC2_PRIVATE_KEY_PATH)

            # Create Logs and scripts folder
            SSH_UTIL.run_command(False, "mkdir -p setup/logs setup/scripts")

            # Copy Scripts to EC2 Instance
            SSH_UTIL.scp_to_machine(local_helper_script_path, remote_helper_script_path)
            SSH_UTIL.scp_to_machine(local_install_script_path, remote_install_script_path)
            SSH_UTIL.scp_to_machine(local_prepare_script_path, remote_prepare_script_path)

            # Run Scripts in EC2 Instance
            SSH_UTIL.run_script(remote_install_script_path, remote_install_logs_path)
            SSH_UTIL.run_script(remote_prepare_script_path, remote_prepare_logs_path, S3_URI, SSM_GIT_PRIVATE_KEY_NAME, AWS_REGION, API_URL, MC_PORT)

        elif command == "stop":
            # Server Shutdown Script Paths
            local_shutdown_script_path = os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], "post_mc_server_shutdown.sh")
            remote_shutdown_script_path = "setup/scripts/post_mc_server_shutdown.sh"
            remote_shutdown_logs_path = "setup/logs/shutdown.log"

            # Helper Function Script paths
            local_helper_script_path = os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], "helper_functions.sh")
            remote_helper_script_path = "setup/scripts/helper_functions.sh"

            # Initilize SSH Util
            SSH_UTIL = SSHUtil(MACHINE_IP, EC2_USERNAME, EC2_PRIVATE_KEY_PATH)

            # Copy Scripts to EC2 Instance
            SSH_UTIL.scp_to_machine(local_helper_script_path, remote_helper_script_path)
            SSH_UTIL.scp_to_machine(local_shutdown_script_path, remote_shutdown_script_path)

            # Run Scripts in EC2 Instance
            SSH_UTIL.run_script(remote_shutdown_script_path, remote_shutdown_logs_path, S3_URI)

            # Check minecraft-world.bundle size - need to add an option for output in ssh_andrun_command.
            mincraft_bundle_path = os.path.join("minecraft-AWS-server", "docker", "minecraft-data", "minecraft-world.bundle")
            mc_world_size = SSH_UTIL.run_command(True, f"stat -c%s {mincraft_bundle_path}")

            # Terraform commands
            TF_MINECRAFT_INFRA = TerraformHelper(GIT_REPO_CONFIG["paths"]["tf_mc_infra"])
            TF_MINECRAFT_INFRA.run_command("destroy")

            # If the minecraft bundle is over a certain size -> start new job to compress it
            check_mc_bundle_size(int(mc_world_size), API_URL)
        elif command == "mc_world_archive":
            # Archive Minecraft World Data Script
            local_archive_mc_script_path = os.path.join(GIT_REPO_CONFIG["paths"]["tf_mc_infra_scripts"], "mc_world_archiver.sh")
            run_script(local_archive_mc_script_path, S3_URI)
        else:
            logger.error("error command not found")
        
        logger.info("Server Handler Completed Successfully")

if __name__ == "__main__":
    manager = ServerManager()
    manager.server_handler(JOB)