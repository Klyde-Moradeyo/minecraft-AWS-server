import boto3
import os
import tempfile
from git import Repo
from python_terraform import Terraform
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    # SSH Key name from system manager parameter store
    ssh_key_name = "dark-mango-bot-private-key" 

    # Repo to clone containing terraform manifests and scripts
    repo = { 
        "url": "https://github.com/klydem11/minecraft-AWS-server.git", 
        "branch": "main",
        "ssh_key": f"{get_git_ssh_key(ssh_key_name)}"
    }

    print(f"repo: {repo}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        git_clone(repo["url"], temp_dir, repo["branch"], repo["ssh_key"])
        os.remove(repo["ssh_key"]) # Remove the SSH key file

        # Directories
        tf_private_key_folder = os.path.join(temp_dir, "terraform", "minecraft_infrastructure", "private-key")
        tf_mc_infra_manifests = os.path.join(temp_dir, "terraform", "minecraft_infrastructure")

        # Ec2 Instance private Key directory
        private_key = create_private_key("terraform_key.pem", tf_private_key_folder)

        # Change to minecraft_infrastrucutre dir
        os.chdir(tf_mc_infra_manifests)
        
lambda_handler("event", "context")


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

def git_clone(repo_url, dir, branch, ssh_key):
    # Set the SSH key environment variable and disable host key checking
    custom_ssh_env = os.environ.copy()
    custom_ssh_env["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

    repo = Repo.clone_from(repo_url, dir, branch=branch, env=custom_ssh_env)
    return

def create_private_key(file_name, directory):
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

    # Save the serialized private key to a file named "private_key.pem" with write binary mode
    file_path = os.path.join(directory, file_name)
    with open(file_path, "wb") as f:
        f.write(private_key_pem)

    os.chmod(file_path, 0o400)

    # Return t he directory of the priv key
    return os.path.abspath(file_path)

