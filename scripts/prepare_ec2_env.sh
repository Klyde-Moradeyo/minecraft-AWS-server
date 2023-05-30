#!/bin/bash

# Title: Prepare Enviornment
# Use: Sets up workspace

set -e
source helper_functions.sh

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
  # Variables
  home_dir="/home/ubuntu"
  git_private_key_path="$home_dir/.ssh/id_rsa"

  repo="git@github.com:Klyde-Moradeyo/minecraft-AWS-server.git"
  repo_branch="main"
  repo_folder="$home_dir/minecraft-AWS-server"

  mc_map_repo="git@github.com:Klyde-Moradeyo/minecraft-world.git"
  mc_map_repo_branch="main"
  mc_map_repo_folder="$repo_folder/docker/minecraft-data/minecraft-world"

  mc_map_s3_bucket="s3://your-bucket-name/minecraft-world.tar.gz"
  mc_map_folder="$repo_folder/docker/minecraft-data/minecraft-world"

  # disable strict host key checking and then git clone relevant repos
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -v -b $repo_branch $repo $repo_folder
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -v -b $mc_map_repo_branch $mc_map_repo $mc_map_repo_folder

  aws s3 cp $mc_map_s3_bucket $home_dir/minecraft-world.tar.gz || { echo 'Failed to download Minecraft world from S3'; exit 1; }
  mkdir -p $mc_map_folder
  tar -xzf $home_dir/minecraft-world.tar.gz -C $mc_map_folder
  rm $home_dir/minecraft-world.tar.gz # Clean up after ourselves

  # Run Docker Compose
  docker_compose_file="$repo_folder/docker"
  docker compose -f "$docker_compose_file/docker-compose.yml" --project-directory "$docker_compose_file" up -d
}

# Call the run function
start=$(date +%s.%N)
check_install
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish