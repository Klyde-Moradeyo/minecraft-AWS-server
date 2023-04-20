#!/bin/bash

# Use: Installs Docker and Docker Compose
# Ref:
#   https://docs.docker.com/engine/install/ubuntu/
#   https://docs.docker.com/compose/install/linux/#install-the-plugin-manually


# Update the package list and install packages to allow apt to use a repository over HTTPS
apt-get update && apt-get install -y sudo

sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg

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
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

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

# Check installation
docker --version
docker compose version