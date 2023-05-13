# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV TERRAFORM_VERSION=1.4.4
ENV AWSCLI_VERSION=2.7.31

# Install necessary packages
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN curl https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -o /tmp/terraform.zip \
    && unzip /tmp/terraform.zip -d /usr/local/bin/ \
    && rm /tmp/terraform.zip

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWSCLI_VERSION}.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm awscliv2.zip

# Verify installations
RUN terraform -v
RUN aws --version
RUN git --version

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*