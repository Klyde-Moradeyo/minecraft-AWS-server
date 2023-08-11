#!/bin/bash

set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/helper_functions.sh"

# Trap the ERR signal
trap 'if [[ $? -ne 0 ]]; then error_handler; fi' EXIT

s3_bucket_path="$1"

echo "=== Configuration Parameters ==="
echo "S3 Bucket Path: $s3_bucket_path"
echo "==============================="

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <s3_bucket_path>"
  exit 1
fi

function cp_dir {
    local source="$1"
    local destination="$2"
    local exclude='.git/'

    echo "Copying '$source' to '$destination'"
    rsync -a --exclude=$exclude "$source/" "$destination/"
}

function run_git_cmd {
    local repo_dir="$1"
    shift
    git -C "$repo_dir" "$@" 
}

function git_clone {
    local source="$1"
    local destination="$2"

    echo "Git Clone '$source' to '$destination'"
    git clone $source $destination
}

function git_commit {
    local repo_dir="$1"
    local commit_msg="$2"

    echo "Commit Message: '$commit_msg' to Repo: '$repo_dir'"
    run_git_cmd "$repo_dir" add .
    run_git_cmd "$repo_dir" commit -m "$commit_msg"
}

function get_commit_msg {
    local repo_dir="$1"

    run_git_cmd "$repo_dir" log -1 --pretty=format:"%s"
}

function  get_commit_hashes {
    local repo_dir="$1" 

    # Get the SHA of the initial commit
    local initial_commit=$(git -C "$repo_dir" rev-list --max-parents=0 HEAD)

    # Get the SHA of the latest commit on master
    local latest_commit=$(git -C "$repo_dir" rev-parse master)

    # Print the values in a way the caller can capture
    echo "$initial_commit $latest_commit"
}

function create_git_bundle {
    local repo_dir="$1"
    local output="$2"
    echo "Creating git bundle for Repo: '$repo_dir'"
    run_git_cmd "$repo_dir" bundle create "$output" --all
}

function create_repo {
    local repo_dir="$1"
    local rm_dir="${2:-FALSE}"

    if [ "$rm_dir" == "TRUE" ]; then
        echo "Removing old '$repo_dir'"
        rm -rf "$repo_dir" 
    fi
    
    echo "Creating new '$repo_dir'"
    mkdir -p "$repo_dir"
    git init "$repo_dir"

    configure_git "$repo_dir"
}

function configure_git_pack_settings {
    if git config --global pack.windowMemory "400m" &&
       git config --global pack.packSizeLimit "100m" &&
       git config --global pack.threads "1"; then
        echo "Git pack settings successfully configured."
    else
        echo "Error: Failed to configure Git pack settings."
        return 1
    fi
}

function s3_download {
    local s3_object_dir="$1"
    local output_object_dir="$2"
    
    echo "Downloading from s3 '$s3_object_dir' to '$output_object_dir'"
    aws s3 cp "$s3_object_dir" "$output_object_dir"
}
function s3_push {
    local s3_object_dir="$1"
    local s3_bucket_path="$2"
    
    echo "Pushing '$s3_object_dir' to bucket '$s3_bucket_path'"
    aws s3 cp "$s3_object_dir" "$s3_bucket_path"
}

function check_s3_file_exist {
    local s3_bucket_path="$1"
    local file="$2"

    # Use AWS CLI to check if the file exists
    local result=$(aws s3 ls "${s3_bucket_path}/${file}" 2>&1)
    local status=$?

    # If the AWS CLI command failed or the result contains the word "error" (case-insensitive)
    if [ "${status}" -ne 0 ] || [[ "${result,,}" == *"error"* ]]; then
        echo "Error checking if '${file}' exists: ${result}"
        exit 1
    fi

    # If the result is empty, the file does not exist
    if [ -z "${result}" ]; then
        echo "'${file}' does not exist in S3 bucket."
        return 3
    else
        echo "'${file}' exists in S3 bucket."
        return 0
    fi
}

function check_file_exists {
    # Check each argument for existence as a file
    for file in "$@"; do
        if [[ ! -f "$file" ]]; then
            echo "Error: File '$file' does not exist."
            exit 1
        fi
    done
}

function run {
    local s3_bucket_path="$1" # this should be a parameter from fargate task"

    working_dir="./tmp/"

    s3_file_name="minecraft-world.bundle"
    s3_file_dir="$working_dir/$s3_file_name"

    s3_archive_file_name="minecraft-world-archive.bundle"
    s3_archive_file_dir="$working_dir/$s3_archive_file_name"

    latest_mc_world_repo_dir="$working_dir/${s3_file_name%.bundle}"
    archive_mc_world_repo_dir="$working_dir/${s3_archive_file_name%.bundle}"

    configure_git_pack_settings

    # #### FOR TESTING IF STATEMENT ######
    # rm -rfv $working_dir
    # mkdir -p $latest_mc_world_repo_dir
    # cp ./minecraft-world.bundle "$latest_mc_world_repo_dir.bundle"
    # cp -v ./minecraft-world-archive-diff.bundle "$archive_mc_world_repo_dir.bundle_old"
    # mv -v "$archive_mc_world_repo_dir.bundle_old" "$archive_mc_world_repo_dir.bundle"
    # #######################

    # #### FOR TESTING ELSE STATEMENT ######
    # rm -rfv $working_dir
    # mkdir -p $latest_mc_world_repo_dir
    # cp ./minecraft-world.bundle "$latest_mc_world_repo_dir.bundle"
    #######################
    
    # #### FOR TESTING ######
    # # incrmeental
    # if check_s3_file_exist "$s3_bucket_path" "minecraft-world.bundle"; then
    # #######################
    if check_s3_file_exist "$s3_bucket_path" "$s3_archive_file_name"; then
        echo "Running incremental time build..."
        echo "------------------- Prepare Environment -------------------"
        # Download Bundles
        run_parallel \
            "s3_download \"$s3_bucket_path/$s3_file_name\" \"$latest_mc_world_repo_dir.bundle\"" \
            "s3_download \"$s3_bucket_path/$s3_archive_file_name\" \"$archive_mc_world_repo_dir.bundle\""

        # Clone Repos
        run_parallel \
            "git_clone \"$s3_file_dir\" \"$latest_mc_world_repo_dir\"" \
            "git_clone \"$s3_archive_file_dir\" \"$archive_mc_world_repo_dir\""
        echo "--------------------------------------------------------------"
        
        echo "------------ Add latest commit to archive repo ---------------"
        configure_git "$archive_mc_world_repo_dir"
        cp_dir "$latest_mc_world_repo_dir/" "$archive_mc_world_repo_dir/"

        commit_msg=$(get_commit_msg "$latest_mc_world_repo_dir")
        echo "Latest Commit Message: '$commit_msg'" 

        git_commit "$archive_mc_world_repo_dir" "$commit_msg"
        echo "--------------------------------------------------------------"

        echo "------------------- Recreating latest repo -------------------"
        create_repo "$latest_mc_world_repo_dir" "TRUE"
        cp_dir "$archive_mc_world_repo_dir/" "$latest_mc_world_repo_dir/"
        git_commit "$latest_mc_world_repo_dir" "$commit_msg"
        echo "--------------------------------------------------------------"
    else
        echo "Running first time build..."
        echo "------------------- Prepare Environment -------------------"
        s3_download "$s3_bucket_path/$s3_file_name" "$latest_mc_world_repo_dir.bundle"
        git_clone "$s3_file_dir" "$latest_mc_world_repo_dir"
        rm -rfv "$s3_file_dir"
        read initial_commit_hash latest_commit_hash < <(get_commit_hashes "$latest_mc_world_repo_dir")
        echo "Initial commit hash: $initial_commit_hash"
        echo "Latest commit hash: $latest_commit_hash"
        echo "--------------------------------------------------------------"

        echo "--------------------- Build Archive Repo ---------------------"
        run_git_cmd "$latest_mc_world_repo_dir" checkout -f $initial_commit_hash

        # Get Time and Date of commit
        date_str=$(run_git_cmd "$latest_mc_world_repo_dir" show -s --format="%cd" --date="format:%d/%m/%Y %I:%M %p" HEAD)

        # Create commit_msg based on helper function commit_msg
        base_msg="${commit_msg%: Add Minecraft Data *}"
        initial_commit_msg="${base_msg}: Add Minecraft Data $date_str"
        echo "Initial Commit Message: '$initial_commit_msg'"

        create_repo "$archive_mc_world_repo_dir"
        echo "Creating Initial commit of archive repo..."
        cp_dir "$latest_mc_world_repo_dir/" "$archive_mc_world_repo_dir/"
        git_commit "$archive_mc_world_repo_dir" "$initial_commit_msg"

        echo "Retrieving latest commit of latest repo and adding it to archive repo..."
        run_git_cmd "$latest_mc_world_repo_dir" checkout -f $latest_commit_hash
        latest_commit_msg=$(get_commit_msg "$latest_mc_world_repo_dir")
        cp_dir "$latest_mc_world_repo_dir/" "$archive_mc_world_repo_dir/"
        git_commit "$archive_mc_world_repo_dir" "$latest_commit_msg"
        echo "--------------------------------------------------------------"

        echo "------------------- Recreating latest repo -------------------"
        create_repo "$latest_mc_world_repo_dir" "TRUE"
        cp_dir "$archive_mc_world_repo_dir/" "$latest_mc_world_repo_dir/"
        git_commit "$latest_mc_world_repo_dir" "$commit_msg"
        echo "--------------------------------------------------------------"
    fi
    echo "------------------------ Post Build --------------------------"
    # Archive Repos
    s3_file_output_dir="$latest_mc_world_repo_dir/$s3_file_name"
    s3_archive_file_output_dir="$archive_mc_world_repo_dir/$s3_archive_file_name"

    run_parallel \
        "create_git_bundle \"$latest_mc_world_repo_dir\" \"$s3_file_name\"" \
        "create_git_bundle \"$archive_mc_world_repo_dir\" \"$s3_archive_file_name\""

    check_file_exists "$s3_file_output_dir" "$s3_archive_file_output_dir"
    echo "Bundles Created:"
    echo "- $s3_file_output_dir"
    echo "- $s3_archive_file_output_dir"

    # Push git bundles to s3
    run_parallel \
        "s3_push "$s3_file_output_dir" "$s3_bucket_path"" \
        "s3_push "$s3_archive_file_output_dir" "$s3_bucket_path""
    echo "--------------------------- Done -----------------------------"
}

start=$(date +%s.%N)
run "$s3_bucket_path"
finish=$(date +%s.%N)
get_current_date
calculate_runtime $start $finish