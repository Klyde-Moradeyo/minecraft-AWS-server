#!/bin/bash

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/helper_functions.sh"

# Trap the ERR signa
trap 'if [[ $? -ne 0 ]]; then error_handler; fi' EXIT

s3_bucket_path="$1"

echo "=== Configuration Parameters ==="
echo "S3 Bucket Path: $s3_bucket_path"
echo "==============================="

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <s3_bucket_path>"
  exit 1
fi

stop_docker() {
  local docker_dir="$1"
  echo "Stopping Docker Containers"
  (cd "$docker_dir" && docker compose down)
}

move_monitoring_log() {
  local docker_dir="$1"
  local home_dir="$2"
  echo "Moving Monitoring logs"
  mv "$docker_dir/server_monitoring.log" "$home_dir/setup/logs"
}

delete_docker_dir_except_world() {
  local docker_dir="$1"
  echo "Deleting '$docker_dir' except '.git' file"
  rsync -a --delete --exclude="minecraft-data/world" --exclude=".git" /tmp/empty-dir/ "$docker_dir/"
}

commit_and_push_world() {
  local mc_map_repo_folder="$1"
  local s3_bucket_path="$2"
  local mc_world_bundle_path="$mc_map_repo_folder/minecraft-world.bundle"

  echo "Git Commit'$mc_map_repo_folder'"
  git -C "$mc_map_repo_folder" add .
  # Allow the commit command to fail without stopping the script
  if git -C "$mc_map_repo_folder" commit -m "$commit_msg"; then
    echo "Changes committed successfully"
  else
    echo "No changes to commit"
  fi
  
  echo "Creating Git Bundle: '$mc_world_bundle_path'"
  git -C "$mc_map_repo_folder" bundle create minecraft-world.bundle --all

  echo "Pushing 'minecraft-world.bundle' to '$s3_bucket_path'"
  aws s3 cp "$mc_world_bundle_path" "$s3_bucket_path"
}

zip_and_push_logs() {
  local home_dir="$1"
  local s3_bucket_path="$2"
  local log_file_name="setup_logs.zip"

  echo "Zipping logs '$home_dir/setup/logs'"
  zip -jr setup_logs.zip "$home_dir/setup/logs"

  echo "Pushing '$log_file_name' to '$s3_bucket_path'"
  aws s3 cp setup_logs.zip "$s3_bucket_path"
}

run() {
  local home_dir="/home/ubuntu"
  local docker_dir="$home_dir/minecraft-AWS-server/docker"
  local mc_map_repo_folder="$docker_dir/minecraft-data"

  stop_docker "$docker_dir"
  move_monitoring_log "$docker_dir" "$home_dir"
  delete_docker_dir_except_world "$docker_dir"
  configure_git "$mc_map_repo_folder"
  commit_and_push_world "$mc_map_repo_folder" "$s3_bucket_path"
  zip_and_push_logs "$home_dir" "$s3_bucket_path"
}

start=$(date +%s.%N)
run
finish=$(date +%s.%N)

get_current_date
calculate_runtime $start $finish