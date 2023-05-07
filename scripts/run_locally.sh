#!/bin/bash

# Title: Run Locally
# Use: Run locally on your machine for testing
# Terraform Version: Terraform CLI - Terraform v1.4.4

source helper_functions.sh

mode=$1
environment=${2:-"minecraft_infrastructure"} # set default

mode=$(echo "$mode" | tr '[:upper:]' '[:lower:]')
environment=$(echo "$environment" | tr '[:upper:]' '[:lower:]')

if [[ "$mode" != "apply" && "$mode" != "destroy" && "$mode" != "plan" && "$mode" != "build" ]]; then
    echo "Invalid argument: $mode"
    echo "Usage: $0 [apply|destroy|plan|build(lambda)]"
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
    echo -e "\n"

    cd $mc_infra_dir

    # Private Key Read Only
    sudo chmod 400 ./private-key/terraform-key.pem

    run_mode "$mode"

    # Clean up
    echo -e "\n"
    echo "Clean up:"
    rm -rfv "./scripts"
}

function run_mc_eip_lambda {
    mode=$1
    mc_eip_dir=$2

    if [[ $mode == "build" && "$environment" == "lambda" ]]; then
        lambda_dir="../lambda"

        # Create python packages folder
        while read requirement; do
        module_name=$(echo $requirement | sed -e 's/#.*//' -e 's/[[:space:]]*$//') # Remove any comments (lines starting with #) and whitespace
        if [ -n "$module_name" ]; then  # Check if the line is not empty
            pip install --target $lambda_dir/package "$module_name"
        fi
        done < "$lambda_dir/requirements.txt"

        chmod 644 "$lambda_dir/lambda_function.py" "$lambda_dir/package"
        chmod 755 "$lambda_dir/lambda_function.py" "$lambda_dir/package"
        zip -r $lambda_dir/lambda_deployment "$lambda_dir/lambda_function.py" "$lambda_dir/package"
        rm -rf "$lambda_dir/package"
    else
        cd $mc_eip_dir
        run_mode "$mode"
    fi
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
if [[ "$environment" == "eip" || "$environment" == "lambda" ]]; then
    run_mc_eip_lambda "$mode" "../terraform/eip-lambda"
elif [ "$environment" == "minecraft_infrastructure" ]; then
    run_mc_infra "$mode" "../terraform/minecraft_infrastructure"
else
    echo "Invalid argument"
fi
finish=$(date +%s.%N)
calculate_runtime $start $finish