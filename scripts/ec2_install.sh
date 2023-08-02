#!/bin/bash

# Title: EC2 Install
# Use: Installs Docker, Docker Compose, AWS CLI, and Git
# Ref:
#   https://docs.docker.com/engine/install/ubuntu/
#   https://docs.docker.com/compose/install/linux/#install-the-plugin-manually
#   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $script_dir/helper_functions.sh

# Trap the ERR signal
trap 'error_handler' ERR

# Run the apt-get command 
# DPkg::Lock checks if apt lock is in use - Timeout set to -1 for unlimited. 60 for 60 sec
apt_get() {
  sudo apt-get -o DPkg::Lock::Timeout=-1 "$@"
}

########################
# Dependencies Install #
########################
function install_dependencies {
  apt-get update
  apt-get install -y sudo apt-utils
  apt_get install -y \
    lsof \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    unzip \
    zip \
    bc \
    rsync
}

########################
#    Docker Install    #
########################
function install_docker {
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --yes --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  # Add Docker package repository
  echo "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
  
  apt_get update
  apt_get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io

  install_docker_compose
}

# Docker Compose installation
function install_docker_compose {
  DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
  mkdir -p "$DOCKER_CONFIG/cli-plugins"
  curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o "$DOCKER_CONFIG/cli-plugins/docker-compose"
  chmod +x "$DOCKER_CONFIG/cli-plugins/docker-compose"
}

########################
#    AWS CLI Install   #
########################
function install_aws_cli {
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip -o awscliv2.zip
  ./aws/install
}

########################
#     Install Git      #
########################
function install_git {
  apt_get install git -y
}

########################
#     Post Install     #
########################
function post_install {
    # Remove AWS zip
    rm -rfv aws awscliv2.zip

    echo "-------------------------------------"
    echo "              Installed              "
    echo "-------------------------------------"

    if command -v docker > /dev/null 2>&1; then
        echo "Docker:
              $(docker --version)
              $(docker compose version)"
    else
        echo "Docker: Not Installed"
    fi

    if command -v aws > /dev/null 2>&1; then
        echo "AWS CLI: $(aws --version)"
    else
        echo "AWS CLI: Not Installed"
    fi

    if command -v git > /dev/null 2>&1; then
        echo "GIT: $(git --version)"
    else
        echo "GIT: Not Installed"
    fi
    echo "-------------------------------------"
}

function run {
  install_dependencies

  # Run installations in parallel
  install_docker &
  install_aws_cli &
  install_git & 

  # Wait for all installations to complete
  wait

  post_install
}

# Call the run function
start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish
