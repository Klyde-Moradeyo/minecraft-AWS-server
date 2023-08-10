# Use an official Python runtime as a parent image
FROM python:3.9-slim

WORKDIR /app
COPY . .

# Set environment variables
ENV TERRAFORM_VERSION=1.4.4
ENV AWSCLI_VERSION=2.7.31

# Install necessary packages
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    git \
    rsync \
    bc

# Install Terraform
RUN curl https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -o /tmp/terraform.zip \
    && unzip /tmp/terraform.zip -d /usr/local/bin/ \
    && rm /tmp/terraform.zip

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWSCLI_VERSION}.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rfv awscliv2.zip aws

# Verify installations
RUN terraform -v \
    aws --version \
    git --version

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt 

CMD ["python", "app.py"]