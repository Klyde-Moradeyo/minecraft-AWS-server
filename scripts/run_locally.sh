#!/bin/bash

# Title: Run Locally
# Use: Run locally on your machine for testing
# Terraform Version: Terraform CLI - Terraform v1.4.4

source helper_functions.sh

mode=$1
environment=${2:-"minecraft_infrastructure"} # set default

mode=$(echo "$mode" | tr '[:upper:]' '[:lower:]')
environment=$(echo "$environment" | tr '[:upper:]' '[:lower:]')

if [[ "$mode" != "apply" && "$mode" != "destroy" && "$mode" != "plan" ]]; then
    echo "Invalid argument: $mode"
    echo "Usage: $0 [apply|destroy|plan]"
    exit 1
fi

# Go to the run_locally.sh directory
scripts_dir="$(dirname "$(realpath "$0")")"
cd $scripts_dir

function run_mc_infra {
    mode=$1
    mc_infra_dir=$2

    # Copy Scripts folder to mc infrastructure directory
    echo "Copying files..."
    cp -rfv $scripts_dir $mc_infra_dir
    cp -fv ../terraform/eip/EIP.txt $mc_infra_dir

    cd $mc_infra_dir

    # Private Key Read Only
    chmod 400 ./private-key/terraform-key.pem

    run_mode "$mode"

    # Clean up
    echo "Clean up:"
    rm -rfv "./scripts"
}

function run_mc_eip {
    mode=$1
    mc_eip_dir=$2

    cd $mc_eip_dir
    run_mode "$mode"
}

function run_mode() {
    if [[ ! -d  ".terraform" ]]; then
        terraform init
    fi

    case "$1" in
        "apply")
            echo "Applying changes..."
            terraform apply --auto-approve
            ;;
        "destroy")
            echo "Destroying resources..."
            terraform destroy --auto-approve
            ;;
        "plan")
            echo "Plan..."
            terraform plan
            ;;
    esac
}


start=$(date +%s.%N)
if [ "$environment" == "eip" ]; then
    run_mc_eip "$mode" "../terraform/eip"
elif [ "$environment" == "minecraft_infrastructure" ]; then
    run_mc_infra "$mode" "../terraform/minecraft_infrastructure"
else
    echo "Invalid argument"
fi
finish=$(date +%s.%N)
calculate_runtime $start $finish