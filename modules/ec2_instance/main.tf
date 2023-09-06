########################
#     EC2 Instance     #
########################
// Get latest Ubuntu 22.04AMI
data "aws_ami" "ubuntu" {
  most_recent      = true
  owners           = var.ami_owners

  filter {
    name   = "name"
    values = var.ami
  }

  filter {
    name   = "root-device-type"
    values = var.ami_root_device_type
  }

  filter {
    name   = "virtualization-type"
    values = var.ami_virtualization_type
  }


  filter {
      name   = "architecture"
      values = var.architecture
  }
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 3.0"

  name = "${var.label_id}-ec2"

  # Instance
  ami                    = data.aws_ami.ubuntu.image_id
  instance_type          = var.instance_type
  key_name               = "${var.label_id}-key"

  # Instance Profile
  iam_instance_profile = aws_iam_instance_profile.mc.name

  # Network
  vpc_security_group_ids = [ aws_security_group.minecraft_SG.id ]
  subnet_id              = var.subnet_id
  
  # Monitoring
  monitoring             = true

  // Pre-req install Script
  # user_data = file("scripts/ec2_install.sh")

  tags = var.label_tags
}

data "aws_eip" "mc_public_ip" {
  public_ip = var.public_ip
}

resource "aws_eip_association" "mc_public_ip_to_ec2" {
  depends_on = [ module.ec2_instance ]

  instance_id   = module.ec2_instance.id
  allocation_id = data.aws_eip.mc_public_ip.id
}