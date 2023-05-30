#!/bin/bash

# Title: Helper Functions
# Use: Series of Helper functions for running scripts

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
