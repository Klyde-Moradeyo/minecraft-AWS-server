# minecraft-AWS-server

# PreReq
- IAM User available with Admin access

# How to SSH
chmod 400 ./terraform/minecraft_infrastructure/private-key/terraform-key.pem
sudo ssh-keygen -f "/root/.ssh/known_hosts" -R "$(cat ./terraform/minecraft_infrastructure/EIP.txt)"
sudo ssh -i ./terraform/minecraft_infrastructure/private-key/terraform-key.pem ubuntu@$(cat ./terraform/minecraft_infrastructure/EIP.txt)

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