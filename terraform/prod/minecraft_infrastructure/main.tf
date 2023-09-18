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
  mc_port = data.terraform_remote_state.infra_handler_state.outputs.mc_port
  mc_s3_bucket_arn = data.terraform_remote_state.infra_handler_state.outputs.mc_s3_bucket_arn
  mc_s3_bucket_uri= data.terraform_remote_state.infra_handler_state.outputs.mc_s3_bucket_uri
  vpc_id = data.terraform_remote_state.infra_handler_state.outputs.vpc_id
  subnet_id =  data.terraform_remote_state.infra_handler_state.outputs.subnet_id
  public_ip = data.terraform_remote_state.infra_handler_state.outputs.eip
  ec2_key_pair = data.terraform_remote_state.infra_handler_state.outputs.ec2_key_pair
  label_id = data.terraform_remote_state.infra_handler_state.outputs.label_id
  label_tags = data.terraform_remote_state.infra_handler_state.outputs.label_tags
}

################################
#           Modules            #
################################
module "minecraft_server" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/ec2_instance?ref=TF_0.0.2"
  
  # Terraform Cloud Config
  tf_cloud_org                      = var.tf_cloud_org
  tf_cloud_infra_handler_workspace  = var.tf_cloud_infra_handler_workspace

  # EC2 Instance Config
  ami                              = var.ami
  ami_owners                       = var.ami_owners
  ami_root_device_type             = var.ami_root_device_type
  ami_virtualization_type          = var.ami_virtualization_type
  instance_keypair                 = local.ec2_key_pair
  architecture                     = var.architecture
  instance_type                    = var.instance_type

  # Security group
  mc_port                          = local.mc_port
  allowed_cidrs                    = var.allowed_cidrs

  # IAM
  git_private_key_name             = var.git_private_key_name
  mc_s3_bucket_arn                 = local.mc_s3_bucket_arn

  # Public IP
  public_ip = local.public_ip

  # VPC
  vpc_id                           = local.vpc_id
  subnet_id                        = local.subnet_id

  # Module labels
  label_id                         = local.label_id
  label_tags                       = local.label_tags
}
