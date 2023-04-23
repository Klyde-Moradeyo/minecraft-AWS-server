#!/bin/bash

# Use: Installs Docker, Docker Compose and AWS CLI
# Ref:
#   https://docs.docker.com/engine/install/ubuntu/
#   https://docs.docker.com/compose/install/linux/#install-the-plugin-manually
#   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

get_current_date() {
  local year=$(date +"%Y")
  local month=$(date +"%m")
  local day=$(date +"%d")
  local hour=$(date +"%H")
  local minute=$(date +"%M")
  local second=$(date +"%S")

  echo """
  -----------------------------------------------------------------
  Date: $day/$month/$year $hour:$minute:$second
  -----------------------------------------------------------------
  """
}
get_current_date

# Update the package list and install packages to allow apt to use a repository over HTTPS
apt-get update && apt-get install -y sudo

########################
#    Docker Install    #
########################
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker’s official GPG
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --yes --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker package repository to the list of software sources in the Ubuntu
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io

# Download and install the Compose CLI plugin
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose

# Apply executable permissions 
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Add the ubuntu user to the docker group - Avoids Permision issue while trying to connect to the Docker daemon socket
# sudo usermod -aG docker ubuntu

# Apply group membership changes
# newgrp docker

# Restart ubuntu instance
# <insert reboot>

# Check Docker Docker Compose installation
docker --version
docker compose version

########################
#    AWS CLI Install   #
########################
sudo apt-get install -y \
    unzip 

# Download the latest version of the AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip

# Install the AWS CLI
sudo ./aws/install

# Verify the installation
# aws --version

########################
#     Install Git      #
########################
sudo apt-get install git -y
# git --version

########################
#     Post Install     #
########################
rm -rfv aws awscliv2.zip

# Print Everything that was installed in this script at the end
echo """
    -------------------------------------
    Installed:
        Docker: 
                $(docker --version)
                $(docker compose version)
        AWS-CLI: $(aws --version)
        GIT: $(git --version)
    """

# Echo current Date
get_current_date

