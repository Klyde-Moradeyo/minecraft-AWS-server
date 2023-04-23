# minecraft-AWS-server

# PreReq
- IAM User available with Admin access

# How to SSH
chmod 400 terraform-manifests/private-key/terraform-key.pem
ssh -i ./terraform-manifests/private-key/terraform-key.pem ubuntu@$(terraform output -raw public_ip)
cd terraform-manifests & ssh -i ./private-key/terraform-key.pem ubuntu@$(terraform output -raw public_ip)

# Quick Commands for copy and pasting
terraform destroy --auto-approve
terraform apply --auto-approve

# Running Docker with Current 
docker pull ubuntu:latest
docker run -it --name my-ubuntu-container -v $(pwd):/app ubuntu:latest /bin/bash

# Enhacements
- Static public IP Address for connecting to server
- Server only starts up when a connection is request
- m5.large
- Datapack for vanilla tweeks