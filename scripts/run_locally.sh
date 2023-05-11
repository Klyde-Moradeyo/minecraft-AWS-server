#!/bin/bash

# Title: Run Locally
# Use: Run locally on your machine for testing
# Terraform Version: Terraform CLI - Terraform v1.4.4

set -e 

# Go to the run_locally.sh directory
scripts_dir="$(dirname "$(realpath "$0")")"
cd $scripts_dir

source $scripts_dir/helper_functions.sh

mode=$1
environment=${2:-"minecraft_infrastructure"} # set default

mode=$(echo "$mode" | tr '[:upper:]' '[:lower:]')
environment=$(echo "$environment" | tr '[:upper:]' '[:lower:]')

if [[ "$mode" != "apply" && "$mode" != "destroy" && "$mode" != "plan" && "$mode" != "build" ]]; then
    echo "Invalid argument: $mode"
    echo "Usage: $0 [apply|destroy|plan|build(lambda)]"
    exit 1
fi

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

    lambda_zip="lambda_function_payload.zip"

    if [[ $mode == "build" && "$environment" == "lambda" ]]; then
        lambda_dir="../lambda"
        cd $lambda_dir

        pull_amazonLinux_image
        build_lambda_function $lambda_zip
        build_lambda_terraform_layer "terraform_layer.zip"
        
        package_size=$(du -m "$lambda_zip" | cut -f1)
        if (( package_size > 50 )); then
            echo -e "Warning: \nThe lambda_function_payload is larger than 50 MB \nDoc: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html"
        fi

    else
        cd $mc_eip_dir
        lambda_function_payload_dir="../../lambda/$lambda_zip"

        # Check Size of Lambda payload < 50mb
        package_size=$(du -m "$lambda_function_payload_dir" | cut -f1)
        echo "$lambda_zip size: $package_size"
        if (( package_size > 50 )); then
            echo -e "Warning: \nThe lambda_function_payload is larger than 50 MB \nDoc: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html"
        fi

        run_mode "$mode"
    fi
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


function pull_amazonLinux_image() {
    # Check if docker is running
    if ! docker info >/dev/null 2>&1; then
        echo "Docker daemon is not running. Please start the Docker daemon and try again."
        exit 1
    else
        echo "Docker daemon is running."
    fi

    # Pull the Amazon Linux 2 Docker image
    # Check if the amazonlinux:2 image exists locally
    if ! docker image ls | grep -q 'amazonlinux\s*2'; then
        docker pull amazonlinux:2
    fi
}

function execute_in_amazonLinux() {
    local commands=$1
    # Run a Docker container with the image, and compile git inside the container
    docker run --rm -it -v "$(pwd):/app" amazonlinux:2 /bin/bash -c "$commands"
}

function build_lambda_function() {
    local lambda_zip=$1

    commands="
        # Install required packages
        yum install -y python3-pip zip gcc libffi-devel python3-devel openssl-devel dos2unix unzip

        # Enter app Directory
        cd app

        pip3 install -t package -r requirements.txt

        # Remove lambda zip if it exists 
        if [[ -f "$lambda_zip" ]]; then
            rm -rf $lambda_zip
        fi

        # Make sure files are lambda_function.py is dos2unix
        dos2unix "lambda_function.py" # find . -type f -exec dos2unix {} \;

        chmod 644 "lambda_function.py" "package"
        chmod 755 "lambda_function.py" "package"

        cp lambda_function.py package
        (cd package && zip -r ../$lambda_zip .)

        # Clean up after ourselves
        rm -rf "package"
    "
    execute_in_amazonLinux "$commands"
}

function build_lambda_terraform_layer() {
    terraform_zip=$1

    commands="
        # Install required packages
        yum install -y zip unzip

        # Enter app Directory
        cd app

        # Remove layer zip if it exists 
        if [[ -f "$terraform_zip" ]]; then
            rm -rf $terraform_zip
        fi

        curl -o terraform.zip https://releases.hashicorp.com/terraform/1.4.4/terraform_1.4.4_linux_amd64.zip
        unzip terraform.zip
        mkdir -p tf_lambda_package/bin
        mv terraform tf_lambda_package/bin

        chmod 755 tf_lambda_package/bin/terraform

        (cd tf_lambda_package && zip -r ../$terraform_zip .)

        # Clean up after ourselves
        rm -rf bin terraform.zip
    "
    execute_in_amazonLinux "$commands"
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
