import boto3

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


def lambda_handler(event, context):
    # SSH Key name from system manager parameter store
    ssh_key_name = "dark-mango-bot-private-key" 

    # Repo to clone info
    repo_info = { 
        "url": "https://github.com/klydem11/minecraft-AWS-server.git", 
        "branch": "main",
        "ssh_key": f"{get_git_ssh_key(ssh_key_name)}"
    }

    print(f"REPO_INFO: {repo_info}")




lambda_handler("event", "context")
