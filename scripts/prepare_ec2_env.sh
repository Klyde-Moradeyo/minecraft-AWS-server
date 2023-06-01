#!/bin/bash

# Title: Prepare Enviornment
# Use: Sets up workspace

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $script_dir/helper_functions.sh

s3_bucket_path="$1"

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

  # disable strict host key checking and then git clone relevant repos
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -v -b $repo_branch $repo $repo_folder

  # Copy minecraft world
  mc_map_repo_folder="$repo_folder/docker/minecraft-data/minecraft-world"
  aws s3 cp "$s3_bucket_path" "$home_dir/minecraft-world.tar.gz"  || { echo "Failed to download Minecraft world from S3"; exit 1; }
  mkdir -p "$mc_map_folder"
  tar -xzf "$home_dir/minecraft-world.tar.gz" -C "$mc_map_folder"
  rm "$home_dir/minecraft-world.tar.gz" # Clean up after ourselves

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