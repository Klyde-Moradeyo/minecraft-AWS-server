#!/bin/bash

# Post Minecraft Server Container Close
# Use: Post "terraform destroy" script to be performed on ec2 instance

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $script_dir/helper_functions.sh

s3_bucket_path="$1"

# Trap the ERR signal
trap 'error_handler' ERR

function run {
  home_dir="/home/ubuntu"
  docker_dir="$home_dir/minecraft-AWS-server/docker"
  git_private_key_path="$home_dir/.ssh/id_rsa"
  minecraft_world_repo_dir="$docker_dir/minecraft-data/minecraft-world"
  container_world_repo_dir="$docker_dir/minecraft-data/world"

  # Stop the docker container
  $(cd $docker_dir && docker compose down)

  ########################
  # Save MC world in Git #
  ########################
  # Configure Git user
  git config --global user.email "darkmango444@gmail.com"
  git config --global user.name "dark-mango-bot"

  # Replace world in minecraft-world git repo
  rm -rf $minecraft_world_repo_dir/world
  cp -rf $container_world_repo_dir $minecraft_world_repo_dir

  # Go To minecraft-world repo
  cd "$minecraft_world_repo_dir"

  # Add and commit changes
  git add .
  git commit -m "Auto-commit: Update minecraft data"
  git tag "minecraft-data-update-$(date +"%Y-%m-%d")-time-$(date +"%H-%M-%S")"

  # Push changes to the S3 Bucket
  git bundle create minecraft-world.bundle --all
  aws s3 cp minecraft-world.bundle "$s3_bucket_path"
}

# Call the run function
start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish
exit 0


