# Minecraft AWS Server

![Architecture](https://drive.google.com/file/d/1R-HH4RTJtHzSPCfzCM0l_QNF4swQ2Vv6/view?usp=sharing)

This repository contains the necessary scripts and configurations to set up a Minecraft server on AWS using AWS Fargate for serverless compute. The server integrates with a Discord bot to manage server requests. The purpose of this project is to minimize Minecraft server costs by provisioning infrastructure only when needed. The Discord bot, hosted on Fly.io, allows users to start up and shut down their Minecraft server. After a certain period of inactivity, the Minecraft server automatically shuts down.

## Table of Contents

- [Minecraft AWS Server](#minecraft-aws-server)
  - [Table of Contents](#table-of-contents)
  - [Technologies](#technologies)
- [File Structure](#file-structure)
  - [Dependencies](#dependencies)
  - [Getting Started](#getting-started)
  - [Usage](#usage)
  - [CI/CD](#cicd)
  - [Future Improvements](#future-improvements)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [License](#license)
  - [Where to find me](#where-to-find-me)


## Technologies

This project uses the following technologies:

- HCL (Terraform) for Infrastructure as Code (IaC) in Terraform Cloud.
- Python for AWS Lambda functions, the Discord bot, fargate task, and the Minecraft monitoring script.
- Shell for script automation.
- Docker for containerization.
- Fly.io for hosting the Discord bot.
- AWS ECS Fargate for serverless compute.
- AWS Lambda for serverless functions.
- GitHub Actions for CI/CD.

# File Structure

The folder structure is as follows:

- `discord_bot`: Contains the scripts for running the Discord bot on Fly.io. This takes user requests and sends them to an API in AWS.
- `docker`: A Docker container and volume mount directory for the Minecraft server, along with a monitoring container for monitoring the server.
- `terraform`:
  - `infrastructure_handler`: Contains the Terraform manifests for provisioning the static prerequisite Minecraft server infrastructure.
  - `minecraft_infrastructure`: Contains the Terraform manifests for provisioning the Minecraft server.
- `lambda_function`: This is triggered via an API Gateway to create Fargate instances to provision the Minecraft infrastructure.
- `fargate_task`: This is the Python script responsible for starting/stopping the Minecraft infrastructure.
- `scripts`:
  - `run_locally.sh`: This script is designed to run on a developer's Linux machine (Needs to be updated for the current setup).
  - `helper_functions.sh`: Helper functions to be used by the scripts in this directory.
  - The remaining scripts are for setting up/removing the EC2 instance for running the Minecraft server:
    - `ec2_install.sh`
    - `prepare_ec2_env.sh`
    - `post_mc_server_shutdown.sh`

## Dependencies

This project requires the following tools to be installed:

- **Terraform**: Used to automate the creation of the cloud infrastructure.
- **Terraform Cloud**: Storing the cloud infrastructure's state data.
- **Python**: Required for the AWS Lambda functions and the Discord bot.
- **Docker**: Required to containerize the application and its environment.
- **AWS CLI**: Used to interact with Amazon Web Services.
- **Fly.io CLI**: Used to manage the Discord bot deployment.

To install these dependencies, you can use the following commands:

- Terraform: `https://learn.hashicorp.com/tutorials/terraform/install-cli`
- Terraform Cloud: `app.terraform.io`
- Python: `https://www.python.org/downloads/`
- Docker: `https://docs.docker.com/engine/install/`
- AWS CLI: `https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html`
- Fly.io CLI: `https://fly.io/docs/getting-started/installing-flyctl/`

Once these are installed, you can clone the repository and proceed with the [Getting Started](#getting-started) section.

**I advise you to check the (infrastructure_handler variables.tf)[./terraform/infrastructure_handler/variables.tf] and the (minecraft_infrastructure variables.tf)[./terraform/minecraft_infrastructure/variables.tf] to familiarize yourself with what is required.**

## Getting Started

To get started with this project, you need to have:

- AWS account
- Terraform Cloud account
- Discord bot token
- Fly.io account

This project uses the following environment variables:

- `DISCORD_BOT_TOKEN`: Your Discord bot token.
- `AWS_ACCESS_KEY_ID`: Your AWS access key.
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key.
- `TF_API_TOKEN`: Terraform API Token
- `API_URL`: AWS API Gateway URL
- `SERVER_IP`: Minecraft Server EIP

Fly.io would require the `DISCORD_TOKEN`, `API_URL`, and `SERVER_IP` secrets to be available (Please note that the names are different from the variables above - will fix later).
The `infrastructure_handler` would require secrets set in [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) for the Terraform API Token.
The `minecraft_infrastructure` requires `tf_cloud_org` and `tf_cloud_infra_handler_workspace` set in the (variables.tf)[./terraform/minecraft_infrastructure/variables.tf].

Once you've set these up, you can clone this repository and start using it! 
Start by running `terraform apply` in the [infrastructure_handler folder](./terraform/infrastructure_handler).

## Usage

Interact with the Discord bot to manage the Minecraft server. Here are some commands:

- `!start`: Starts the Minecraft server.
- `!stop`: Stops the Minecraft server.
- `!status`: Checks the status of the Minecraft server.

The Discord Bot only receives queries in its designated discord channel.

## CI/CD

This project uses GitHub Actions for Continuous Integration and Continuous Deployment. 
The CI doesn't actually run any tests, but it builds the necessary components for the server.

## Future Improvements

Here are some areas for potential future development:

- **Multi Minecraft server worlds:** Modify the Discord bot to load up multiple Minecraft worlds and even modded worlds!
- **API Gateway authentication:** The API Gateway is unprotected. Authentication needs to be added.
- **Public Domain for Minecraft server:** It would be more cost-effective to use an AWS public domain rather than an EIP.
- **Automatic Server Startup:** The server only starts up when a connection is requested. This would require the Discord bot to use the user's IP for this.
- **Vanilla Tweaks YAML:** Save S3 storage and pull the latest vanilla tweaks package using `itzg/minecraft` Docker image.
- **Save EC2 Instance Space:** Git is being used to version the Minecraft server. This is inefficient as the binaries could be quite large. An automatic archive is needed once the repo reaches a certain size limit. The archive should go to my OneDrive.
- **Git Bundle:** Speed up git bundle?

## Troubleshooting

If you encounter any issues while setting up or running the Minecraft server, check the following:

- Ensure all your environment variables are set correctly.
- Check the AWS Fargate and Lambda service quotas and increase them if needed.
- Make sure your Discord bot token is correct and the bot has the necessary permissions.

If your issue persists, feel free to open an issue on this GitHub repository.

## Contributing

Contributions to this project are welcome! Feel free to open an issue or a pull request if you find a bug, have a feature request, or want to contribute code.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.

## Where to find me

For any queries, you can message me on LinkedIn at [Klyde Moradeyo](https://www.linkedin.com/in/klyde-moradeyo-349847197/).

Please fix any spelling mistakes in the above README.md for my Minecraft AWS Server Git repository. Give your fix in a code block.
