#!/bin/bash
# Prepare Enviornment

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

# Variables
repo="git@github.com:klydem11/minecraft-AWS-server.git"
repo_branch="main"
repo_folder="$(pwd)/minecraft-tf-AWS-server"

mc_map_repo="git@github.com:klydem11/minecraft-world.git"
mc_map_repo_branch="test-world"
mc_map_repo_folder="$(pwd)/minecraft-world"

# git clone relevant repos
git clone -o StrictHostKeyChecking=no -b $repo $repo_branch $repo_folder
git clone -o StrictHostKeyChecking=no -b $mc_map_repo_branch $mc_map_repo $mc_map_repo_folder

sudo docker compose up -d -e WORLD="$mc_map_repo_folder/world"