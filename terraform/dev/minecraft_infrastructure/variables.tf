########################
#       General        #
########################
variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type = string
  default = "eu-west-2"
}

variable "tf_cloud_org" {
  description = "Terraform Cloud organization name"
  type = string
  default = "mango-dev"
}

variable "tf_cloud_infra_handler_workspace" {
  description = "Terraform Cloud workspace name"
  type = string
  default = "dev-minecraft-infra-handler"
}

########################
#     Minecraft        #
########################
variable "mc_port" {
  description = "TCP port for minecraft"
  type        = number
  default     = 25565
}

variable "mc_backup_freq" {
  description = "How often (mins) to sync to S3"
  type        = number
  default     = 5
}

########################
#       AWS EC2        #
########################
variable "instance_type" {
  description = "EC2 Instance Type"
  type = string
  # default = "t4g.2xlarge" 
  default = "t4g.xlarge" 
  // For tests: default =  "t2.medium" | https://amazon-aws-ec2-pricing-comparison.pcapps.com/
}

variable "ami" {
    type = list(string)
    default = [ "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*" ]
}

variable "ami_owners" {
  description = "The AWS account IDs of the AMI owners."
  type        = list(string)
  default     = [ "099720109477" ]
}

variable "ami_root_device_type" {
  description = "The type of root device used by the AMI."
  type        = list(string)
  default     = [ "ebs" ]
}

variable "ami_virtualization_type" {
  description = "The virtualization type of the AMI."
  type        = list(string)
  default     = [ "hvm" ]
}

variable "architecture" {
    type = list(string)
    default = [ "arm64" ]
}

variable "network_interface_id" {
  type = string
  default = "network_id_from_aws"
}

########################
#    Systems Manager   #
########################
variable "git_private_key_name" {
  description = "Private Key name for Github SSH in Systems Manager Parameter Store"
  type        = string
  default     = "dark-mango-bot-private-key"
}

variable "ec2_private_key_name" {
  description = "Private Key name for Github SSH in Systems Manager Parameter Store"
  type        = string
  default     = "/mc_server/private_key"
}

########################
#   Security Groups    #
########################
variable "allowed_cidrs" {
  description = "Allow these CIDR blocks to the server - default is the Universe"
  type        = string
  default     = "0.0.0.0/0" // https://cidr.xyz/
}

########################
#        VPC           #
########################
variable "vpc_id" {
  description = "VPC for security group"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "VPC subnet id to place the instance"
  type        = string
  default     = ""
}