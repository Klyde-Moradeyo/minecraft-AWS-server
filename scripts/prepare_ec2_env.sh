#!/bin/bash

# Title: Prepare Enviornment
# Use: Sets up workspace

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $script_dir/helper_functions.sh

s3_bucket_path="$1"
git_private_key_name="$2"
aws_region="$3"

echo $s3_bucket_path
echo $git_private_key_name
echo $aws_region

# Trap the ERR signal
trap 'error_handler' ERR

function check_install {
  for cmd in aws tar git docker; do
    if ! command -v $cmd &> /dev/null; then
      echo "Error: $cmd is not installed."
      exit 1
    fi
  done
}

function run {
  # Set up git creds
  aws ssm get-parameter --name "$git_private_key_name" --with-decryption --region "$aws_region" --query "Parameter.Value" --output text > ~/.ssh/id_rsa
  chmod 600 ~/.ssh/id_rsa
  ssh-keyscan github.com >> ~/.ssh/known_hosts

  # Variables
  home_dir="/home/ubuntu"
  git_private_key_path="$home_dir/.ssh/id_rsa"

  repo="git@github.com:Klyde-Moradeyo/minecraft-AWS-server.git"
  repo_branch="main"
  repo_folder="$home_dir/minecraft-AWS-server"

  # disable strict host key checking and then git clone relevant repos
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -v -b $repo_branch $repo $repo_folder

  # clean up unused files - We only need the docker folder
  mkdir /tmp/empty-dir
  rsync -a --delete --exclude=docker /tmp/empty-dir/ $repo_folder/ # Use rsync to delete everything in $repo_folder except for $repo_folder/docker

  mc_map_repo_folder="$repo_folder/docker/minecraft-data"
  repo_world_folder="$repo_folder/docker/minecraft-data/minecraft-world/world"

  # Copy minecraft world from S3
  aws s3 cp "$s3_bucket_path/minecraft-world.bundle" "$home_dir/minecraft-world.bundle" || { echo "Failed to download Minecraft world from S3"; exit 1; }
  mkdir -p "$mc_map_repo_folder"
  git clone "$home_dir/minecraft-world.bundle" "$mc_map_repo_folder"
  rm -rf "$home_dir/minecraft-world.bundle" # Clean up after ourselves

  # Run Docker Compose
  docker_compose_file="$repo_folder/docker"
  docker compose -f "$docker_compose_file/docker-compose.yml" --project-directory "$docker_compose_file" up -d

  # clean packages
  apt-get clean
  apt autoremove
  rm -rf /var/lib/apt/lists/*
}

# Call the run function
start=$(date +%s.%N)
check_install
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish