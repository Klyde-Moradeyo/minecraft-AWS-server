#!/bin/bash

# Post Minecraft Server Container Close
# Use: Post "terraform destroy" script to be performed on ec2 instance

source helper_functions.sh

function run {
  home_dir="/home/ubuntu"
  git_private_key_path="$home_dir/.ssh/id_rsa"
  minecraft_world_repo_dir="$home_dir/minecraft-tf-AWS-server/docker/minecraft-data/minecraft-world"
  container_world_repo_dir="$home_dir/minecraft-tf-AWS-server/docker/minecraft-data/world"

  # Stop the docker container
  $(cd $home_dir/minecraft-tf-AWS-server && docker compose down)

  ########################
  # Save MC world in Git #
  ########################
  # Configure Git user
  git config --global user.email "darkmango444@gmail.com"
  git config --global user.name "dark-mango-bot"

  # Replace world in minecraft-world git repo
  rm -rfv $minecraft_world_repo_dir/world
  cp -rfv $container_world_repo_dir $minecraft_world_repo_dir

  # Go To minecraft-world repo
  cd "$minecraft_world_repo_dir"

  # Add and commit changes
  git add .
  git commit -m "Auto-commit: Update minecraft data"
  git tag $(date +"%Y-%m-%d-%H-%M-%S")

  # Push changes to the remote repository
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git push origin
}

# Call the run function
start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish


