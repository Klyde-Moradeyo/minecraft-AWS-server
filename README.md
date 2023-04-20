# minecraft-AWS-server

# PreReq
- IAM User available with Admin access

# How to SSH
chmod 400 terraform-manifests/private-key/terraform-key.pem
ssh -i terraform-manifests/private-key/terraform-key.pem ubuntu@<public-ip-address>


# Enhacements
- Static public IP Address for connecting to server
- Server only starts up when a connection is request