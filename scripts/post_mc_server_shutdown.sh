#!/bin/bash

# Post Minecraft Server Container Close
# Use: Post "terraform destroy" script to be performed on ec2 instance

set -e
source /home/ubuntu/setup/scripts/helper_functions.sh

ec2_log_output_dir="/home/ubuntu/minecraft-AWS-server/docker/minecraft-data/minecraft-world/logs/post_mc_server_shutdown.log"
exec > $ec2_log_output_dir # directs all stdout to the file
exec 2>&1 # directs stderr to the same place as stdout

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
  git tag $(date +"%Y-%m-%d-%H-%M-%S")

  # Push changes to the remote repository
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git push origin
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git push origin --tags
}

# Call the run function
start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish
exit 0


