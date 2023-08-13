
########################
#       Labels         #
########################
module "label" {
  source   = "cloudposse/label/null"
  version = "0.25.0"

  namespace   = var.namespace
  stage       = var.environment
  name        = var.name
  delimiter   = "-"
  label_order = ["environment", "stage", "name", "attributes"]
  tags        = merge(var.tags, local.tf_tags)
}

################################
#   Infra Handler Outputs      #
################################
data "terraform_remote_state" "infra_handler_state" {
  backend = "remote"

  config = {
    organization = var.tf_cloud_org
    workspaces = {
      name = var.tf_cloud_infra_handler_workspace
    }
  }
}

locals {
  mc_s3_bucket_arn = data.terraform_remote_state.infra_handler_state.outputs.mc_s3_bucket_arn
  mc_s3_bucket_uri= data.terraform_remote_state.infra_handler_state.outputs.mc_s3_bucket_uri
}

data "aws_eip" "mc_public_ip" {
  public_ip = data.terraform_remote_state.infra_handler_state.outputs.eip
}

resource "aws_eip_association" "mc_public_ip_to_ec2" {
  depends_on = [ module.ec2_instance ]

  instance_id   = module.ec2_instance.id
  allocation_id = data.aws_eip.mc_public_ip.id
}

########################
#     EC2 Instance     #
########################
# EC2 private key
data "aws_ssm_parameter" "private_key" {
  name = "/mc_server/private_key"
}

// Get latest Ubuntu 22.04AMI
data "aws_ami" "ubuntu" {
  most_recent      = true
  owners           = ["099720109477"]

  filter {
    name   = "name"
    values = [ var.ami ]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
      name   = "architecture"
      values = [ var.architecture ]
  }
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 3.0"

  name = "${var.name}-public"

  # Spot Instance
  # create_spot_instance = true
  # spot_price           = "0.60"
  # spot_type            = "persistent"

  # Instance
  ami                    = data.aws_ami.ubuntu.image_id
  instance_type          = var.instance_type
  key_name               = var.instance_keypair

  # Instance Profile
  iam_instance_profile = aws_iam_instance_profile.mc.name

  # Network
  vpc_security_group_ids = [ aws_security_group.minecraft_SG.id ]
  subnet_id              = local.subnet_id
  
  # Monitoring
  monitoring             = true

  // Pre-req install Script
  # user_data = file("scripts/ec2_install.sh")

  tags = module.label.tags
}

// Set-up Ec2 Pre-reqs
# locals {
#   ec2_scripts = {
#     helper_functions            = "./scripts/helper_functions.sh"
#     ec2_install                 = "./scripts/ec2_install.sh"
#     prepare_ec2_env             = "./scripts/prepare_ec2_env.sh"
#     post_mc_server_shutdown     = "./scripts/post_mc_server_shutdown.sh"
#   }
# }

# resource "null_resource" "copy_scripts" {
#   for_each = local.ec2_scripts

#   depends_on = [ aws_eip_association.mc_public_ip_to_ec2 ]

#   provisioner "file" {
#     source      = each.value
#     destination = "/home/ubuntu/${each.key}.sh"

#     connection {
#       type        = "ssh"
#       user        = "ubuntu"
#       private_key = data.aws_ssm_parameter.private_key.value
#       host        = data.aws_eip.mc_public_ip.public_ip
#     }
#   }
# }

# resource "null_resource" "setup_ec2" {
#   depends_on = [ null_resource.copy_scripts ]

#   provisioner "remote-exec" {
#     inline = [
#       "#!/bin/bash",
#       "mkdir -p /home/ubuntu/setup/scripts /home/ubuntu/setup/logs",
#       "mv /home/ubuntu/{ec2_install,helper_functions,prepare_ec2_env,post_mc_server_shutdown}.sh /home/ubuntu/setup/scripts",
#       "chmod +x /home/ubuntu/setup/scripts/{ec2_install,helper_functions,prepare_ec2_env,post_mc_server_shutdown}.sh",
#       "sudo /home/ubuntu/setup/scripts/ec2_install.sh > /home/ubuntu/setup/logs/install.log", # Run Ec2 Install
#       "aws ssm get-parameter --name \"${var.git_private_key_name}\" --with-decryption --region \"${var.aws_region}\" --query \"Parameter.Value\" --output text > ~/.ssh/id_rsa", # Get git private key
#       "chmod 600 ~/.ssh/id_rsa",
#       "ssh-keyscan github.com >> ~/.ssh/known_hosts",
#       "sudo /home/ubuntu/setup/scripts/prepare_ec2_env.sh \"${local.mc_s3_bucket_uri}\" > /home/ubuntu/setup/logs/prepare_ec2_env.log" # Run Ec2 Prepare Env
#     ]

#     connection {
#       type        = "ssh"
#       user        = "ubuntu"
#       private_key = data.aws_ssm_parameter.private_key.value
#       host        = data.aws_eip.mc_public_ip.public_ip
#     }
#   } 
# }

# # Ec2 before destroy 
# resource "null_resource" "post_mc_server_close" {
#   depends_on = [ module.ec2_instance ]

#   # Use a trigger to recreate the null_resource 
#   # when the EC2 instance is replaced
#   triggers = {
#     instance_id = module.ec2_instance.id
#   }

#   provisioner "local-exec" {
#     when    = destroy # Only execute on destruction of resource
#     command = <<-EOT
#       ssh -v -i ./private-key/terraform-key.pem -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ubuntu@52.56.39.89 "\
#         sudo chmod +x /home/ubuntu/setup/scripts/post_mc_server_shutdown.sh && \
#         sudo /home/ubuntu/setup/scripts/post_mc_server_shutdown.sh \"s3://minecraft-s3-xclhectq\"; exit"
#     EOT
#   }
# }

########################
#   Security Groups    #
########################
resource "aws_security_group" "minecraft_SG" {
  name        = "${var.name}-sg"
  description = "Minecraft Security Group Allow SSH and TCP"
  vpc_id      = local.vpc_id // default VPC

  # Ingress rule for SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    description = "SSH"
    cidr_blocks = [ var.allowed_cidrs ]
  }

  # Ingress rule for Minecraft server
  ingress {
    description      = "Minecraft Server"
    from_port        = var.mc_port
    to_port          = var.mc_port
    protocol         = "tcp"
    cidr_blocks      = [ var.allowed_cidrs ]
  }

  // Allow all outgoing traffic without any restrictions
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = module.label.tags
}