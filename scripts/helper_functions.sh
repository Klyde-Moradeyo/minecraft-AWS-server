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

run_parallel() {
    local cmd_prefix=""
    local pids=() 

    # Check for sudo flag
    if [[ $1 == "-s" || $1 == "--sudo" ]]; then
        cmd_prefix="sudo "
        shift # Shift arguments to remove the flag
    fi

    # For each argument passed to the function
    for cmd in "$@"; do
        local full_cmd="${cmd_prefix}${cmd}"
        echo "[$!] assigned to $full_cmd"
        eval "$full_cmd" & # Execute the command in the background
        pids+=($!) # Save the process ID
    done

    # For each child process ID
    for pid in ${pids[*]}; do
        # Wait for the process to complete and capture its exit status
        local exit_status
        wait $pid || exit_status=$?

        # If the process failed (non-zero exit status)
        if ((exit_status != 0)); then
            echo "Command with PID $pid failed with exit status $exit_status."
            exit $exit_status
        fi
    done
}

get_current_date