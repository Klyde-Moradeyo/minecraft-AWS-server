#!/bin/bash

# Title: Run Locally
# Use: Run locally on your machine for testing
# Terraform Version: Terraform CLI - Terraform v1.4.4

source helper_functions.sh

function run {
    mode=$1
    if [[ "$mode" != "apply" && "$mode" != "destroy" && "$mode" != "plan" ]]; then
        echo "Invalid argument: $mode"
        echo "Usage: $0 [apply|destroy|plan]"
        exit 1
    fi

    # Go to the run_locally.sh directory
    script_dir="$(dirname "$(realpath "$0")")"
    cd $script_dir

    # variables
    scripts_dir="../scripts"
    mc_infra_dir="../terraform/minecraft_infrastructure"


    # Copy Scripts folder to mc infrastructure directory
    echo "Copying scripts..."
    cp -rfv $scripts_dir $mc_infra_dir

    cd $mc_infra_dir

    if [[ ! -d  ".terraform" ]]; then
        terraform init
    fi

    echo -e "\n"
    # If the argument is valid, proceed with the chosen action
    case "$mode" in
        "apply")
            echo "Applying changes..."
            # cp -fv ../eip/EIP.txt .
            terraform apply --auto-approve
            ;;
        "destroy")
            echo "Destroying resources..."
            terraform destroy --auto-approve
            # rm -rfv ec2_public_ip.txt
            ;;
        "plan")
            terraform plan
            ;;
    esac
    echo -e "\n"

    # Clean up
    echo "Clean up:"
    rm -rfv "./scripts"
}

# Call the function from file1.sh
start=$(date +%s.%N)
run "$1"
finish=$(date +%s.%N)

calculate_runtime $start $finish


