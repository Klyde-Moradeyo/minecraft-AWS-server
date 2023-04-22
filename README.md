# minecraft-AWS-server

# PreReq
- IAM User available with Admin access

# How to SSH
chmod 400 terraform-manifests/private-key/terraform-key.pem
ssh -i ./terraform-manifests/private-key/terraform-key.pem ubuntu@<public-ip-address>

cd terraform-manifests & ssh -i ./private-key/terraform-key.pem ubuntu@<public-ip-address>

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


aws ssm get-parameter --name "${var.private_key_name}" --with-decryption --region "${var.region}" --query "Parameter.Value" --output text > /home/ec2-user/private_key.pem
aws ssm get-parameter --name "dark-mango-bot-private-key" --with-decryption --region "eu-west-2" --query "Parameter.Value" --output text > /home/ubuntu/private_key.pem

              chmod 600 /home/ec2-user/private_key.pem
              chown ec2-user:ec2-user /home/ec2-user/private_key.pem