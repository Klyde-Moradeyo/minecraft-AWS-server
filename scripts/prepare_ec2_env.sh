#!/bin/bash

# Title: Prepare Enviornment
# Use: Sets up workspace

source helper_functions.sh

function run {
  # Variables
  home_dir="/home/ubuntu"
  git_private_key_path="$home_dir/.ssh/id_rsa"

  repo="git@github.com:klydem11/minecraft-AWS-server.git"
  repo_branch="main"
  repo_folder="$home_dir/minecraft-tf-AWS-server"

  mc_map_repo="git@github.com:klydem11/minecraft-world.git"
  mc_map_repo_branch="main"
  mc_map_repo_folder="$repo_folder/minecraft-data/minecraft-world"

  # disable strict host key checking and then git clone relevant repos
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -b $repo_branch $repo $repo_folder
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -b $mc_map_repo_branch $mc_map_repo $mc_map_repo_folder

  # Run Docker Compose
  docker_compose_file="$repo_folder/docker"
  docker-compose -f "$docker_compose_file/docker-compose.yml" --project-directory "$docker_compose_file" up -d
}

# Call the run function
start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish