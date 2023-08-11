#!/bin/bash

# Title: Helper Functions
# Use: Series of Helper functions for running scripts

commit_msg="Auto-commit: Add Minecraft Data $(date +"%d/%m/%Y") $(date +"%I:%M %p")"

function get_current_date() {
    local year=$(date +"%Y")
    local month=$(date +"%m")
    local day=$(date +"%d")
    local hour=$(date +"%H")
    local minute=$(date +"%M")
    local second=$(date +"%S")

    echo "-----------------------------------------------------------------"
    echo "Date: $day/$month/$year"
    echo "Time: $hour:$minute:$second"
    echo "-----------------------------------------------------------------"
}

function calculate_runtime() {
    start=$1
    finish=$2

    runtime=$(printf "%.2f\n" $(echo "$finish - $start" | bc))
    minutes=$(echo "$runtime / 60" | bc)
    seconds=$(echo "$runtime % 60" | bc)

    echo "-----------------------------------------------------------------"
    echo "Execution time: ${minutes}m ${seconds}s"
    echo "-----------------------------------------------------------------"
}

function error_handler {
    # Print an error message
    echo "An error occurred while executing the script." >&2
}

function check_pid {
    local pid=$1
    local error_message=$2
    wait $pid || { echo "$error_message"; exit 1; }
}

function configure_git {
  local directory="$1"
  local git_email="mango-bot@mango.com"
  local username="dark-mango-bot"
  
  echo "Configuring Git for $directory..."
  git -C "$directory" config user.email "$git_email"
  git -C "$directory" config user.name "$username"
}

function run_parallel() {
    # Array to store child procexit_satuss IDs
    local pids=() 

    # For each argument passed to the function
    for cmd in "$@"; do
        echo "[$!] assigned to $cmd"
        eval "$cmd" & # Execute the command in the background
        pids+=($!) # Save the procexit_satuss ID
    done

    # For each child procexit_satuss ID
    for pid in ${pids[*]}; do
        # Wait for the procexit_satus to complete and capture its exit status
        local exit_satus
        wait $pid || exit_satus=$?

        # If the procexit_satuss failed (non-zero exit status)
        if ((exit_satus != 0)); then
            echo "Command with PID $pid failed with exit status $exit_satus."
            # Optionally, exit if one command fails
            exit $exit_satus
        fi
    done
}

get_current_date