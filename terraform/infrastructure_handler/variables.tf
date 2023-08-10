
########################
#     General AWS      #
########################
variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type = string
  default = "eu-west-2"
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
#       S3 Bucket      #
########################
variable "bucket_force_destroy" {
  description = "Boolean that indicates all objects should be deleted from the bucket"
  type        = bool
  default     = false
}

########################
#    Systems Manager   #
########################
variable "git_private_key_name" {
  description = "Private Key name for Github SSH in Systems Manager Parameter Store"
  type        = string
  default     = "dark-mango-bot-private-key"
}

variable "discord_token_name" {
  description = "Discord token name in Systems Manager Parameter Store"
  type        = string
  default     = "discord-mango-machine-bot"
}

variable "terraform_token_name" {
  description = "Terraform token name in Systems Manager Parameter Store"
  type        = string
  default     = "terraform-cloud-user-api"
}

########################
#         ECR          #
########################
variable "ecr_repo_name" {
  description = "ECR Repo Name"
  type        = string
  default     = "mc_infra_runner"
}

variable "ecr_image_name" {
  description = "ECR Repo Name"
  type        = string
  default     = "mc_infra_runner_img"
}

########################
#         ECS          #
########################
variable "ecs_cpu_limit" {
  description = "CPU Resource limit for container level and task level"
  type        = string
  default     = "256"
}

variable "ecs_memory_limit" {
  description = "Memory Resource limit for container and task level"
  type        = string
  default     = "1024"
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






