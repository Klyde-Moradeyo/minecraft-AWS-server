#!/bin/bash

# Title: Run Locally
# Use: Run locally on your machine for testing
# Terraform Version: Terraform CLI - Terraform v1.4.4

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

    if [[ $mode == "build" && "$environment" == "lambda" ]]; then
        lambda_dir="../lambda"
        cd $lambda_dir
        
        # Create python packages folder
        pip install -t package -r requirements.txt

        # Add git to deployment package
        create_git_executable

        # Make sure files are lambda_function.py is dos2unix
        dos2unix "lambda_function.py" # find . -type f -exec dos2unix {} \;

        if ! test -e "git"; then
            echo "Error: Git Binary Missing"
            exit 1
        else
            mv -f git package/bin
        fi
        mv -rf template package/template

        chmod 644 "lambda_function.py" "package"
        chmod 755 "lambda_function.py" "package"

        cp lambda_function.py package
        (cd package && zip -r ../lambda_function_payload.zip .)
        
        package_size=$(du -m "lambda_function_payload.zip" | cut -f1)
        if (( package_size > 50 )); then
            echo -e "Warning: \nThe lambda_function_payload is larger than 50 MB \nDoc: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html"
        else
            # rm -rf "$lambda_dir/package" -- Commented Out For Testing
            true
        fi

    else
        cd $mc_eip_dir
        lambda_function_payload_dir="../../lambda/lambda_function_payload.zip"

        # Check Size of Lambda payload < 50mb
        package_size=$(du -m "$lambda_function_payload_dir" | cut -f1)
        if (( package_size > 50 )); then
            echo -e "Warning: \nThe lambda_function_payload is larger than 50 MB \nDoc: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html"
        fi

        run_mode "$mode"
        # rm -rfv lambda_function_payload.zip
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

function create_git_executable() {
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

    # Run a Docker container with the image, and compile git inside the container
    if docker run --rm -it -v "$(pwd):/output" amazonlinux:2 /bin/bash -c "
        # Install required packages
        yum groupinstall -y 'Development Tools'
        yum install -y wget openssl-devel curl-devel expat-devel gettext-devel zlib-devel perl-ExtUtils-MakeMaker

        # Download git source code
        GIT_VERSION='2.34.0' # You can change this to the version you want
        wget https://github.com/git/git/archive/refs/tags/v\${GIT_VERSION}.tar.gz
        tar -xf v\${GIT_VERSION}.tar.gz
        cd git-\${GIT_VERSION}

        # Compile git with libcurl and OpenSSL support
        make configure
        ./configure --prefix=/usr/local \
                    CFLAGS='\${CFLAGS} -I/usr/local/include' \
                    LDFLAGS='-L/usr/local/lib' \
                    --with-curl \
                    --with-openssl
        make

        if ! test -e 'git'; then
            echo 'Error: Docker - Git Binary Missing'
            exit 1
        fi

        # Copy the git binary to the desired output location
        cp git /output/git
    "; then
        echo "git executable build successful"
    else
        echo "Failed to create git executable"
        exit 1
    fi
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
unzip lambda_function_payload.zip -d lambda_function_payload/ 
calculate_runtime $start $finish
