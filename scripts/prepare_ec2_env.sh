#!/bin/bash

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/helper_functions.sh" || error_handler "Failed to source helper functions"

# Trap the ERR signal
trap 'if [[ $? -ne 0 ]]; then error_handler; fi' EXIT

s3_bucket_path="$1"
git_private_key_name="$2"
aws_region="$3"
api_url="$4"
rcon_port="$5"

echo "=== Configuration Parameters ==="
echo "S3 Bucket Path: $s3_bucket_path"
echo "Git Private Key Name: $git_private_key_name"
echo "AWS Region: $aws_region"
echo "API URL: $api_url"
echo "RCON Port: $rcon_port"
echo "==============================="

if [[ $# -ne 5 ]]; then
  echo "Usage: $0 <s3_bucket_path> <git_private_key_name> <aws_region> <api_url> <rcon_port>"
  exit 1
fi

function check_install {
  for cmd in aws tar git docker; do
    if ! command -v $cmd &> /dev/null; then
      echo "Error: $cmd is not installed."
      exit 1
    fi
  done
}

create_env_file() {
    local directory=$1
    local api_url=$2
    local rcon_port=$3
    local promtheus_port="9200" # To be replaced by a parameter from terraform files
    local env_file_path="$directory/.env"

    # Define the environment variables
    declare -A env_variables
    env_variables["API_URL"]="$api_url"
    env_variables["RCON_PORT"]="$rcon_port"
    env_variables["PROMETHEUS_PORT"]="$promtheus_port"

    # Create the .env file
    echo "# Generated .env file" > "$env_file_path"
    for key in "${!env_variables[@]}"; do
        echo "$key=${env_variables[$key]}" >> "$env_file_path"
    done

    echo ".env file created at $env_file_path"
}

function mc_server_icon() {
  local docker_compose_file_path="$1"

  # Check if docker_compose_file_path is not empty
  if [[ -z "${docker_compose_file_path}" ]]; then
    echo "Error: No Docker Compose file path provided"
    return 1
  fi

  # Check if the Docker Compose file exists
  if [[ ! -f "${docker_compose_file_path}" ]]; then
    echo "Error: File ${docker_compose_file_path} does not exist"
    return 1
  fi

  # List of URLs
  local urls=(
    'https://drive.google.com/uc?id=1cKMBJ9YR3nco-eAd2H-N1Rrg3UkAdMRx'
    'https://drive.google.com/uc?id=1M-U5Id6gjk3IUcvJv9kXRvWA7x9PTBpE'
    'https://drive.google.com/uc?id=18zAABmF2vimdQ_275c4llR9GTKdLNX7D'
    'https://drive.google.com/uc?id=1whYab8byQ3pW5aVW70iCu-EBi6p_VdVn'
    'https://drive.google.com/uc?id=1rMjv3bdBIQVmbjUnWcfKkiBd8jPbp9UX'
    'https://drive.google.com/uc?id=1VvTbz130Q2vmu7CSFP-ztoij04ZKkt4O'
    'https://drive.google.com/uc?id=1LkfW4ERVI-Y2r74KoyA-gGLYM-k2fnsz'
  )

  # Select a random URL from the list
  local icon_url="${urls[RANDOM % ${#urls[@]}]}"

  # Replace "xxICONxx" with the selected URL in the Docker Compose file
  sed -i.bak "s|xxICONxx|$icon_url|g" "${docker_compose_file_path}"
}

function setup_git_creds {
  ssh_key_file=$(mktemp)
  aws ssm get-parameter --name "$git_private_key_name" --with-decryption --region "$aws_region" --query "Parameter.Value" --output text > "$ssh_key_file" || error_handler "Failed to fetch SSH key"
  chmod 600 "$ssh_key_file"
  ssh-keyscan github.com >> $ssh_key_file
  echo "$ssh_key_file"
}

function clean_repo {
  # clean up unused files - We only need the docker folder
  mkdir /tmp/empty-dir
  rsync -a --delete --exclude=docker /tmp/empty-dir/ $repo_folder/ # Use rsync to delete everything in $repo_folder except for $repo_folder/docker
}

function setup_minecraft_world {
  local s3_bucket_path="$1"
  local home_dir="$2"
  local mc_map_repo_folder="$3"

  mkdir -p "$mc_map_repo_folder"
  git clone "$home_dir/minecraft-world.bundle" "$mc_map_repo_folder"
  rm -rf "$home_dir/minecraft-world.bundle" # Clean up after ourselves
}

function setup_docker_environment {
  local docker_folder="$1"
  local api_url="$2"
  local rcon_port="$3"

  # Create .env file for server monitoring
  create_env_file "$docker_folder" "$api_url" "$rcon_port"

  # Choose a random server image
  mc_server_icon "$docker_folder/docker-compose.yml"
}

function run_docker_compose {
  local docker_compose_file="$1"

  # Run Docker Compose
  docker compose -f "$docker_compose_file/docker-compose.yml" --project-directory "$docker_compose_file" up -d
}

function clean_packages {
  local git_private_key_path="$1"

  apt-get clean
  apt autoremove
  rm -rf /var/lib/apt/lists/*
  rm -f "$git_private_key_path"
}

function parallel_download_and_clone {
  local git_private_key_path="$1"
  local s3_bucket_path="$2"
  local home_dir="$3"
  local repo_folder="$4"

  repo="git@github.com:Klyde-Moradeyo/minecraft-AWS-server.git"
  repo_branch="main"

  # Start git cloning in the background
  GIT_SSH_COMMAND="ssh -i $git_private_key_path -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone -v -b $repo_branch $repo $repo_folder &
  git_clone_pid=$!

  # Start downloading Minecraft world in the background
  aws s3 cp "$s3_bucket_path/minecraft-world.bundle" "$home_dir/minecraft-world.bundle" &
  mc_world_download_pid=$!

  # Wait for both background processes to complete
  check_pid $mc_world_download_pid "Failed to download Minecraft world from S3"
  check_pid $git_clone_pid "Failed to clone the git repository"
}

function run {
  # Variables
  home_dir="/home/ubuntu"
  git_private_key_path=$(setup_git_creds)
  repo="git@github.com:Klyde-Moradeyo/minecraft-AWS-server.git"
  repo_branch="main"
  repo_folder="$home_dir/minecraft-AWS-server"
  docker_folder="$repo_folder/docker"
  docker_compose_file="$repo_folder/docker"
  mc_map_repo_folder="$docker_folder/minecraft-data"

  # Download minecraft world and Clone git Repo in parallel
  parallel_download_and_clone "$git_private_key_path" "$s3_bucket_path" "$home_dir" "$repo_folder"

  # clean repository
  clean_repo

  # Setup Minecraft world
  setup_minecraft_world "$s3_bucket_path" "$home_dir" "$mc_map_repo_folder"

  # Setup Docker environment
  setup_docker_environment "$docker_folder" "$api_url" "$rcon_port"

  # Run Docker Compose
  run_docker_compose "$docker_compose_file"

  # Clean packages
  clean_packages "$git_private_key_path"
}

# Call the run function
start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish
