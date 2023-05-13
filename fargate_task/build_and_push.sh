#!/bin/bash

set -e 

# Get the ECR repository URL as a command line argument
ECR_REPO_URL=${1:-"847399026905.dkr.ecr.eu-west-2.amazonaws.com/mc_infra_runner"}

# The name of the Docker image you want to create
IMAGE_NAME=${2:-"mc_infra_runner"}

# Get a unique identifier for the image tag (current timestamp)
IMAGE_TAG="latest"

AWS_REGION="eu-west-2"

# Build the Docker image
echo "Building Docker image $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

# Tag the Docker image
echo "Tagging Docker image with $ECR_REPO_URL..."
docker tag $IMAGE_NAME:latest $ECR_REPO_URL:$IMAGE_TAG

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL

# Push the Docker image to the ECR repository
echo "Pushing Docker image to ECR repository..."
docker push $ECR_REPO_URL:$IMAGE_TAG

echo "Done."
