########################
#         Tags         #
########################
variable "label_id" {
  description = "ID from labels module"
  type        = string
}

variable "label_tags" {
  description = "Tags from labels module"
  type        = map(string)
}

########################
#         ECR          #
########################
variable "ecr_repo_name" {
  description = "ECR Repo Name"
  type        = string
}

########################
#         ECS          #
########################
variable "ecs_cpu_limit" {
  description = "CPU Resource limit for container level and task level"
}

variable "ecs_memory_limit" {
  description = "Memory Resource limit for container and task level"
  type        = string
}

variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type = string
}

########################
#    Systems Manager   #
########################
variable "git_private_key_name" {
  description = "Private Key name for Github SSH in Systems Manager Parameter Store"
  type        = string
}

variable "ec2_private_key_name" {
  description = "Auto Generated Private key name in Systems Manager Parameter Store"
  type        = string
}

variable "bot_command_name" {
  description = "Bot Command in Systems Manager Parameter Store"
  type        = string
}

variable "terraform_token_name" {
  description = "Terraform token name in Systems Manager Parameter Store"
  type        = string
}

########################
#         IAM          #
########################
variable "s3_bucket_arns" {
  description = "S3 Bucket arns that the fargate container requires access to"
  type        = string
}
