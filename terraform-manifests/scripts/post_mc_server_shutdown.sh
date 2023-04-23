#!/bin/bash

# Post Minecraft Server Container Close
# Use: Post "terraform destroy" script to be performed on ec2 instance

home_dir="/home/ubuntu"
git_private_key_path="$home_dir/.ssh/id_rsa"
minecraft_world_repo_dir="$home_dir/minecraft-tf-AWS-server/minecraft-data/minecraft-world"
container_world_repo_dir="$home_dir/minecraft-tf-AWS-server/minecraft-data/world"

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

# Stop the docker container
$(cd $home_dir/minecraft-tf-AWS-server && docker compose down)

########################
# Save MC world in Git #
########################
# Configure Git user
git config --global user.email "darkmango444@gmail.com"
git config --global user.name "dark-mango-bot"

# Rebase branch
GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git rebase origin

# Replace world in minecraft-world git repo
rm -rf $minecraft_world_repo_dir/world
cp $container_world_repo_dir $minecraft_world_repo_dir

# Go To minecraft-world repo
cd "$minecraft_world_repo_dir"

# Add and commit changes
git add .
git commit -m "Auto-commit: Update minecraft world date $(date +"%d"):$(date +"%m"):$(date +"%Y") $(date +"%H"):$(date +"%M")"

# Push changes to the remote repository
GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git push origin

get_current_date


