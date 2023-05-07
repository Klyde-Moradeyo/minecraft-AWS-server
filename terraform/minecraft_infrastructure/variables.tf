########################
#     Minecraft        #
########################
variable "mc_port" {
  description = "TCP port for minecraft"
  type        = number
  default     = 25565
}

variable "mc_version" {
  description = "Which version of minecraft to install"
  type        = string
  default     = "latest"
}

variable "mc_backup_freq" {
  description = "How often (mins) to sync to S3"
  type        = number
  default     = 5
}

########################
#     General AWS      #
########################
variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type = string
  default = "eu-west-2"
}

########################
#       AWS EC2        #
########################
variable "instance_type" {
  description = "EC2 Instnace Type"
  type = string
  default = "t2.medium"	// "t3.micro"
}

variable "ami" {
    type = string
    default = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
}

variable "instance_keypair" {
  description = "AWS EC2 Key Pair that need to be associated with EC2 Instance"
  type = string
  default = "terraform-key"
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

########################
#   Security Groups    #
########################
variable "allowed_cidrs" {
  description = "Allow these CIDR blocks to the server - default is the Universe"
  type        = string
  default     = "0.0.0.0/0" // https://cidr.xyz/
}


########################
#       S3 Bucket      #
########################
variable "bucket_force_destroy" {
  description = "Boolean that indicates all objects should be deleted from the bucket"
  type        = bool
  default     = false
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

########################
#         Tags         #
########################
variable "name" {
  description = "Name to use for servers, tags, etc (e.g. minecraft)"
  type        = string
  default     = "minecraft"
}

variable "namespace" {
  description = "Namespace, which could be your organization name or abbreviation, e.g. 'eg' or 'cp'"
  type        = string
  default     = "games"
}

variable "environment" {
  description = "Environment, e.g. 'prod', 'staging', 'dev', 'pre-prod', 'UAT'"
  type        = string
  default     = "prod"
}

variable "tags" {
  description = "Any extra tags to assign to objects"
  type        = map
  default     = {}
}






