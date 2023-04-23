#!/bin/bash

# Post Minecraft Server Container Close
# Use: Post "terraform destroy" script to be performed on ec2 instance

home_dir="/home/ubuntu"

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
$(cd $home_dir/minecraft-tf-AWS-server && docker-compose down)

########################
# Save MC world in Git #
########################
# Configure Git user
git config --global user.email "darkmango444@gmail.com"
git config --global user.name "dark-mango-bot"

# Go To minecraft-world repo
cd "$home_dir/minecraft-tf-AWS-server/minecraft-data/minecraft-world"

# Add and commit changes
git add .
git commit -m "Auto-commit: Update minecraft world date $(date +"%d"):$(date +"%m"):$(date +"%Y") $(date +"%H"):$(date +"%M")"

# Push changes to the remote repository
git push origin

get_current_date


