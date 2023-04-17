
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

########################
#     EC2 Instance     #
########################
// Get latest Ubuntu 22.04AMI
data "aws_ami" "ubuntu" {
  most_recent      = true
  owners           = ["099720109477"]

  filter {
    name   = "name"
    values = [var.ami]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}


module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 3.0"

  name = "${var.name}-public"

  # Spot Instance
  create_spot_instance = true
  spot_price           = "0.60"
  spot_type            = "persistent"

  # Instance
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.instance_keypair

  # Netowork
  vpc_security_group_ids = [ "sg-12345678" ]
  subnet_id              = "subnet-eddcdzz4"
  
  # Monitoring
  monitoring             = true

  tags = module.label.tags
}        