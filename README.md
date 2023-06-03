# Table of Contents
- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Languages and Technologies](#languages-and-technologies)
- [File Structure](#file-structure)
- [File Structure Tree](#file-structure-tree)
- [Enhancements](#enhancements)
  - [Notes](#notes)

# Overview
This repo is for provisioning a minecraft server on Amazon Web Services (AWS). It contains the necessary scripts and configurations to set up a Minecraft server on AWS. The server utilizes AWS Fargate for serverless compute and integrates with a Discord bot to manage server requests.

The intention of this project was to save money on a minecraft server through provisioning the required infrastructure only when it is required by it's users. At a high level, a discord bot is running on for free in fly.io, user's can use this discord bot to start up and shutdown their minecraft server. The minecraft server will also shutdown after a specified time of inactivity.

# Languages and Technologies
This project is built using:
- HCL (Terraform) for infrastructure as code
- Python for AWS Lambda functions and the Discord bot
- Shell for script automation
- Docker for containerization

# File Structure
The folder structure is as following:
- `discord_bot`: Contains the scripts for running the discord bot on fly.io, this takes user requests and sends it to an API in AWS
- `docker`: contains the docker container and volume mount directory of the minecraft server
- `terraform` -> 
    - `infrastructure_handler`: Contains the terraform manifests for provisioning the static pre-requisite infrastucture
    - `minecraft_infrastructure`: Contains the terraform manifests for provisioning the minecraft server 
- `lambda_function`: This is triggered via an API to create and read fargate instances to provision the minecraft infrastructure
- `fargate_task`: This is is the python script responsible for managing the state of the minecraft infrastructure
- `scripts`: this contains:
    - `run_locally.sh`: This is a scripts designed to run on a developer's linux machine
    - `helper_functions.sh`: Helper functions to be used by the scripts in this directory
    - The remaining scripts are for setting up the ec2 instance for running the minecraft server:
        - `ec2_install.sh`
        - `prepare_ec2_env.sh`
        - `post_mc_server_shutdown.sh`

# File Structure Tree

```
    minecraft-AWS-Server
    ├── discord_bot
    │   ├── discord_bot.py
    │   └── requirements.txt
    ├── docker
    │   ├── docker-compose.yml
    │   └── minecraft-data
    ├── fargate_task
    │   ├── app.py
    │   ├── build_and_push.sh
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── test.py
    ├── lambda_function
    │   ├── lambda_function_payload.zip
    │   ├── lambda_function.py
    │   └── requirements.txt
    ├── LICENSE
    ├── README.md
    ├── scripts
    │   ├── ec2_install.sh
    │   ├── helper_functions.sh
    │   ├── post_mc_server_shutdown.sh
    │   ├── prepare_ec2_env.sh
    │   └── run_locally.sh
    └── terraform
        ├── infrastructure_handler
        │   ├── api_gateway.tf
        │   ├── ecs.tf
        │   ├── eip.tf
        │   ├── lambda.tf
        │   ├── network.tf
        │   ├── outputs.tf
        │   ├── terraform.tfstate
        │   ├── terraform.tfstate.backup
        │   ├── variables.tf
        │   └── versions.tf
        └── minecraft_infrastructure
            ├── EIP.txt
            ├── iam.tf
            ├── main.tf
            ├── outputs.tf
            ├── private-key
            │   └── terraform-key.pem.secret
            ├── terraform.tfstate
            ├── terraform.tfstate.backup
            ├── variables.tf
            ├── versions.tf
            └── vpc.tf
```

# Enhancements
The Minecraft server has the following enhancements:
- Static public IP Address for connecting to the server
- Server only starts up when a connection is requested
- Utilizes m5.large instance type
- Includes json datapack for vanilla tweaks
- Kubernetes cluster to manage the servers
- split up fargate execution perms and runtime perms
- use python tenacity module to add retries to the fargate task 

## Notes
- To get cross workspace access in terraform cloud, you need to give a workspace permision to view another.
